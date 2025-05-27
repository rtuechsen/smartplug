"""Contains the SmartplugApp class which stores most of the data for the
backend and also handles background tasks the REST API does not handle.

TODO: more details ???
"""

import time
import datetime
import threading
from django.apps import AppConfig
from rest_framework import status
import django_eventstream
from .error_handler import BackendError
from .logger import Logger
from .tree_item import TreeItem, TreeItemDevice, TreeItemGroup
from .mqtt_client import MQTTClient
from .device_tree import DeviceTree
from .admin_settings import (
    USE_SWITCHING_DELAYS,
    SWITCHING_TOGGLE_DELAY,
    INRUSH_CURRENT_DELAY,
)


class SmartplugApp(AppConfig):
    """The main class for storing data about devices and groups as well as
    their state. Also handles background tasks the REST API does not handle.

    This module is registered in the django settings as an app. This
    means it is instanciated by django when the server starts.

    It reads config.json and holds the hierarchy of devices and groups
    as well as their current state. It is used by the REST API to get or
    manipulate data from the device hierarchy. It holds the mqtt client
    to communicate with the devices.

    Functions that answer calls from the REST API should raise
    BackendError's. Other function might do this as well if it makes
    sense.

    Apps in Django usually define and initialize all their attributes as
    class attributes. When Django has loaded all models the
    ready()-function of all apps are called.
    """

    ## The name of the app (required by Django).
    name: str = "smartplug_app"

    # TODO: remove, used for debugging only
    _background_task_started: bool = False

    _device_tree: DeviceTree

    ## A mutex to avoid race conditions on the device tree. Needed because
    ## async calls from the REST API are possible. ALWAYS lock this mutex
    ## when reading or manipulating the device tree!
    _device_tree_mutex: threading.Lock = threading.Lock()

    _last_switch_on_date_time: datetime.datetime = datetime.datetime.now()

    _last_switch_on_date_time_mutex: threading.Lock = threading.Lock()

    ## The logger instance (singleton) to log events and errors.
    _logger: Logger = Logger()

    _mqtt_client: MQTTClient

    def ready(self) -> None:

        SmartplugApp._logger.info("Server was started.")

        with SmartplugApp._device_tree_mutex:
            SmartplugApp._device_tree = DeviceTree("./config.json")

        SmartplugApp._mqtt_client = MQTTClient(
            on_update_callback=self.handle_mqtt_update
        )

        # TODO: remove, used for debugging only
        # if not SmartplugApp._background_task_started:
        #     SmartplugApp._background_task_started = True
        #     thread = threading.Thread(target=self.loop, daemon=True)
        #     thread.start()

    # TODO: remove, used for debugging only
    # def loop(self) -> None:
    #     time.sleep(2)
    #     while True:
    #         time.sleep(2)
    #         # TODO: remove, used for debugging only
    #         # self.change_device_tree_randomly(10)
    #         django_eventstream.send_event(
    #             "device_tree_update", "message", self.get_device_tree_dicts()
    #         )

    def get_device_tree_dicts(self) -> list[dict]:
        """Function to answer a call to /gettree, returns the current state of
        the tree.

        @return A hierarchy of dictionaries and lists representing the current
        state of the device tree.
        """
        with SmartplugApp._device_tree_mutex:
            tree_dicts = SmartplugApp._device_tree.get_device_tree_dicts()

        return tree_dicts

    def _filter_devices_not_allowed_to_switch_on(
        self,
        devices_to_switch: list[TreeItemDevice],
    ):

        # re-evaluating tree should not be necessary while resolving deps
        # (because devices cannot depend on groups)

        resolved_states: dict[str, bool] = {}

        # only need to make sure that all the devices are allowed to switch,
        # e.g. not switching monitor on without PC on

        # traverse deps backwards: first leaves with no own deps, then their
        # listeners

        # returns the new state a device
        def will_be_on(device: TreeItemDevice):

            # check if device has already been checked, return that value in
            # that case
            if device.deviceId in resolved_states:
                return resolved_states[device.deviceId]

            if device.get_isOn() is True:
                resolved_states[device.deviceId] = True
                return True

            # device is OFF -> only way it might be ON afterwards if it is
            # amoung devices_to_switch
            if device not in devices_to_switch:
                resolved_states[device.deviceId] = False
                return False

            # device is OFF, but is scheduled to be switched ON -> can still
            # fail if all dependencies are off

            if len(device.turn_off_if_all_in_list_are_off) == 0:
                resolved_states[device.deviceId] = True
                return True

            trigger_states: list[bool] = [
                will_be_on(trigger_device)
                for trigger_device in device.turn_off_if_all_in_list_are_off
            ]

            if all(state is False for state in trigger_states):
                # do not allow to switch on if all dependencies are off
                # will also choose this path if device has no dependencies
                resolved_states[device.deviceId] = False
                return False

            resolved_states[device.deviceId] = True
            return True

        devices_allowed_to_switch_on = []

        for device in devices_to_switch:
            if will_be_on(device):
                devices_allowed_to_switch_on.append(device)

        return devices_allowed_to_switch_on

    def handle_mqtt_update(self, deviceId: str, kind: str, value: bool):
        """TODO"""

        device: TreeItemDevice = SmartplugApp._device_tree.get_device(deviceId)

        if device is None:
            SmartplugApp._logger.warn(
                f"Received an update for deviceId {deviceId} via MQTT, but "
                "deviceId is not known."
            )
            return

        with SmartplugApp._device_tree_mutex:

            if kind == "isAvailable":
                device.set_isAvailable(value)
            elif kind == "isOn":
                device.set_isOn(value)

        django_eventstream.send_event(
            "device_tree_update", "message", self.get_device_tree_dicts()
        )

        if kind == "isAvailable":
            return

        if value is True:
            return

        # a device was turned OFF -> need to check switching dependencies

        # only do single dependency step! further deps will be handled once
        # their isOn state has been confirmed

        for (
            listener_device
        ) in device.other_devices_listening_for_this_device_switching_off:

            if listener_device.get_isOn() is False:
                # already off, no action needed
                continue

            # listener_device is ON, need to check its dependencies to see if
            # it should be turned OFF

            trigger_states = [
                trigger_device.get_isOn()
                for trigger_device in listener_device.turn_off_if_all_in_list_are_off
            ]

            if all(state is False for state in trigger_states):
                # TODO: is simply choosing index 0 here okay? if so, write comment!
                SmartplugApp.switch(self, listener_device.ids[0], False)

    def switch(self, id: str, desired_isOn: bool) -> None:
        """Function to answer a call to /switch, turns devices and groups
        on/off according to the request.

        @param id The id of the device or group to switch.

        @param desired_isOn A boolean indicating if the item should be turned
        on (True) or off (False). Ignores PEP8 naming convention to match the
        name of the variable across the project.
        """

        # TODO: break function into smaller parts

        tree_item: TreeItem = SmartplugApp._device_tree.get_item(id)

        if id is None:
            raise BackendError(
                f"Specified id {id} does not exist.",
                status.HTTP_400_BAD_REQUEST,
                "Specified id does not exist.",
            )

        devices_to_switch: list[TreeItemDevice] = (
            self._choose_devices_to_switch(tree_item, desired_isOn)
        )

        # if requests are dropped due to SWITCHING_TOGGLE_DELAY
        were_requests_dropped: bool = False

        for device in devices_to_switch:

            if self._try_switching_device(device, desired_isOn) is True:
                were_requests_dropped = True

        # TODO: add info about delay value
        if were_requests_dropped:
            raise BackendError(
                f"Some switch requests were not executed in order to comply "
                f"with the per device switching delay of "
                f"{SWITCHING_TOGGLE_DELAY} seconds.",
                status.HTTP_409_CONFLICT,
                f"Some switch requests were not executed in order to comply "
                f"with the per device switching delay of "
                f"{SWITCHING_TOGGLE_DELAY} seconds.",
            )

    def _try_switching_device(
        self, device: TreeItemDevice, desired_isOn: bool
    ) -> bool:

        # TODO: remove, development code
        if USE_SWITCHING_DELAYS is False:
            SmartplugApp._mqtt_client.switch(device.deviceId, desired_isOn)
            return False

        with SmartplugApp._device_tree_mutex:

            if device.get_isOn() is desired_isOn:
                # isOn is already in desired state, no switching needed
                return

            now = datetime.datetime.now()

            # need to save last 'switch ON time' (mutex), wait until below delay
            # TODO: only delay between device switches, not at beginning or end
            # of request - Todo already done ???
            if desired_isOn:
                # only delay switching when switching ON (no inrush
                # current when switching OFF)
                with SmartplugApp._last_switch_on_date_time_mutex:

                    time_passed_since_last_switch_on: datetime.timedelta = (
                        now - SmartplugApp._last_switch_on_date_time
                    )

                    if (
                        time_passed_since_last_switch_on.seconds
                        < INRUSH_CURRENT_DELAY
                    ):

                        time.sleep(
                            INRUSH_CURRENT_DELAY
                            - time_passed_since_last_switch_on.seconds
                        )

                    SmartplugApp._last_switch_on_date_time = (
                        datetime.datetime.now()
                    )

            now = datetime.datetime.now()
            time_passed_since_last_switch_of_current_item: (
                datetime.timedelta
            ) = (now - device.time_last_switched)

            if (
                time_passed_since_last_switch_of_current_item
                < datetime.timedelta(seconds=SWITCHING_TOGGLE_DELAY)
            ):
                return True

            device.time_last_switched = now

        SmartplugApp._mqtt_client.switch(device.deviceId, desired_isOn)

        return False

    def _choose_devices_to_switch(
        self, tree_item: TreeItem, desired_isOn: bool
    ) -> list[TreeItemDevice]:

        def get_devices(tree_item: TreeItem):

            if isinstance(tree_item, TreeItemDevice):
                return [tree_item]

            elif isinstance(tree_item, TreeItemGroup):
                devices = []
                for child in tree_item.children:
                    devices.extend(get_devices(child))
                return devices

        all_devices: list[TreeItemDevice] = get_devices(tree_item)

        devices_to_switch: list[TreeItemDevice] = [
            device
            for device in all_devices
            if device.get_isOn() is not desired_isOn
        ]

        if desired_isOn is True:
            devices_to_switch: list[TreeItemDevice] = (
                self._filter_devices_not_allowed_to_switch_on(
                    devices_to_switch
                )
            )

        return devices_to_switch
