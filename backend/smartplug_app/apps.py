"""Contains the SmartplugApp class which stores most of the data for the
backend.
"""

import time
from datetime import datetime, timedelta
from threading import Lock
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
    SWITCHING_TOGGLE_DELAY_SECONDS,
    INRUSH_CURRENT_DELAY_SECONDS,
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

    ## The device tree stores the hierarchy of groups and devices as well as
    ## their current state.
    _device_tree: DeviceTree

    ## A mutex to avoid race conditions on _device_tree.
    _device_tree_mutex: Lock = Lock()

    ## This variable stores the last point of time when a device was switched
    ## ON. This is used to delay turning on devices and reduce inrush current.
    _last_switch_on_date_time: datetime = datetime.now()

    ## A mutex to avoid race conditions on _last_switch_on_date_time.
    _last_switch_on_date_time_mutex: Lock = Lock()

    ## The logger instance (singleton) used to log events and errors.
    _logger: Logger = Logger()

    ## An instance of MQTTClient which is used to communicate with devices via
    ## MQTT.
    _mqtt_client: MQTTClient

    def ready(self) -> None:
        """This function is called from Django as soon as the django registry
        is fully populated. It is used to initialize device tree and establish
        a connection to the devices in the network.
        """

        SmartplugApp._logger.info("Server was started.")

        # Load the configuration of the device tree from file.
        with SmartplugApp._device_tree_mutex:
            SmartplugApp._device_tree = DeviceTree("./config.json")

        # Establish a connection to the devices in the network using MQTT.
        # Afterwards the MQTT broker will send information about the state of
        # each device.
        SmartplugApp._mqtt_client = MQTTClient(
            on_update_callback=self.handle_mqtt_update
        )

    def get_device_tree_dicts(self) -> list[dict]:
        """Function to answer a clients call to /gettree, returns the current
        state of the device tree.

        @return A hierarchy of dictionaries and lists representing the current
        state of the device tree.
        """
        with SmartplugApp._device_tree_mutex:
            tree_dicts = SmartplugApp._device_tree.get_device_tree_dicts()

        return tree_dicts

    def _filter_devices_not_allowed_to_switch_on(
        self,
        devices_to_switch: list[TreeItemDevice],
    ) -> None:
        """Function to filter devices from a list of devices to switch ON that
        are not allowed to switch ON.

        Devices can be configured to turn OFF if certain other devices are OFF.
        This functions ensures that those dependencies are always satisfied.

        @param devices_to_switch A list of devices which are requested to be
        switched ON.
        """

        # A dictionary that stores the resolved isOn state (ON/OFF) for a
        # deviceId i.e. the state it should have after executing the switch
        # while still satisfying the defined dependencies between devices.
        # Used to avoid resolving devices multiple times.
        resolved_states_per_deviceId: dict[str, bool] = {}

        # We only need to make sure that all the devices are allowed to switch,
        # e.g. not switching monitor ON without PC ON

        # The idea is to traverse the dependencies backwards: first the leaves
        # with no own deps, then their listeners and so on.

        def will_be_on(device: TreeItemDevice) -> bool:
            """This function returns the resolved state of a given device.

            @param device The device which state should be resolved.

            @return THe state of isOn that the given device should have after
            executing the switch.
            """

            # Check if the device has already been checked, return that value
            # in that case.
            if device.deviceId in resolved_states_per_deviceId:
                return resolved_states_per_deviceId[device.deviceId]

            # No further actions needed if the device is alreay ON.
            if device.get_isOn() is True:
                resolved_states_per_deviceId[device.deviceId] = True
                return True

            # The device is OFF -> the only way it might be ON afterwards is,
            # if it is amoung devices_to_switch.
            if device not in devices_to_switch:
                resolved_states_per_deviceId[device.deviceId] = False
                return False

            # The device is OFF, but is scheduled to be switched ON -> can
            # still fail to switch ON if all its dependencies are OFF.

            # If the device has no dependencies there is no reason not to
            # switch ON.
            if len(device.turn_off_if_all_in_list_are_off) == 0:
                resolved_states_per_deviceId[device.deviceId] = True
                return True

            # At this point we need to recursively check all the device's
            # dependencies. trigger_states are the resolved states of the
            # device's dependencies.
            trigger_states: list[bool] = [
                will_be_on(trigger_device)
                for trigger_device in device.turn_off_if_all_in_list_are_off
            ]

            if all(state is False for state in trigger_states):
                # Do not allow to switch ON if all dependencies are OFF.
                resolved_states_per_deviceId[device.deviceId] = False
                return False

            resolved_states_per_deviceId[device.deviceId] = True
            return True

        devices_allowed_to_switch_on = []

        for device in devices_to_switch:
            if will_be_on(device):
                devices_allowed_to_switch_on.append(device)

        return devices_allowed_to_switch_on

    def handle_mqtt_update(
        self, deviceId: str, kind: str, value: bool
    ) -> None:
        """Function to handle incoming MQTT messages.

        This function is used by the MQTTClient to inform the SmartplugApp
        about changes to device states. It is also called when the SmartplugApp
        establishes a connection to the MQTT broker.

        @param deviceId The deviceId of the device which state has changed.

        @param kind The kind of the state change, one of: 'isOn', 'isAvailable'.

        @param value The new value of the state.
        """

        device: TreeItemDevice = SmartplugApp._device_tree.get_device(deviceId)

        if device is None:
            SmartplugApp._logger.warn(
                f"Received an update for deviceId {deviceId} via MQTT, but "
                "the deviceId is unknown."
            )
            return

        with SmartplugApp._device_tree_mutex:

            if kind == "isAvailable":
                device.set_isAvailable(value)
            elif kind == "isOn":
                device.set_isOn(value)

        # Notify the connected users about the state change.
        django_eventstream.send_event(
            "default",
            "device_tree_update",
            self.get_device_tree_dicts(),
        )

        # After a device has changed switched OFF, other devices might need to
        # switch OFF as well to satisfy the dependencies between them.

        if kind == "isAvailable":
            return

        if value is True:
            return

        # The device was turned OFF -> we need to check its dependencies.

        # We only resolve a single level of these dependencies at a time. If
        # switching OFF devices should lead to more devices required to switch
        # OFF, those will be handled once we receive the signal that the former
        # have actually switched OFF.

        for (
            listener_device
        ) in device.other_devices_listening_for_this_device_switching_off:

            if listener_device.get_isOn() is False:
                # The device is already off, no action needed.
                continue

            # The device is ON, we need to check its dependencies to see if it
            # should be turned OFF.

            trigger_states: list[bool] = [
                trigger_device.get_isOn()
                for trigger_device in listener_device.turn_off_if_all_in_list_are_off
            ]

            if all(state is False for state in trigger_states):
                # All dependencies are off -> this device should be switche OFF
                # as well.
                if len(listener_device.ids) == 0:
                    SmartplugApp._logger.warn(
                        "A device is required to switch OFF, but it is not "
                        "used in the device tree."
                    )

                # Note regarding listener_device.ids[0]: simply choosing index
                # 0 when selecting an id for the device is okay, as all ids of
                # the device refer to this device.
                SmartplugApp.switch(self, listener_device.ids[0], False)

    def switch(self, id: str, desired_isOn: bool) -> None:
        """Function to answer a clients call to /switch, it turns devices and
        groups ON/OFF according to the request.

        @param id The id of the device or group to switch.

        @param desired_isOn A boolean indicating if the item should be turned
        ON (True) or OFF (False).
        """

        tree_item: TreeItem = SmartplugApp._device_tree.get_item(id)

        if tree_item is None:
            raise BackendError(
                f"Specified id {id} does not exist. This can also happen if a "
                f"device exists in the config but is not used in the tree.",
                status.HTTP_400_BAD_REQUEST,
                "Specified id does not exist.",
            )

        devices_to_switch: list[TreeItemDevice] = (
            self._choose_devices_to_switch(tree_item, desired_isOn)
        )

        # We keep track if requests are dropped in order to comply with the
        # switching delay of that device.
        were_requests_dropped: bool = False

        for device in devices_to_switch:

            if self._try_switching_device(device, desired_isOn) is True:
                were_requests_dropped = True

        if were_requests_dropped:
            raise BackendError(
                f"Some switch requests were not executed in order to comply "
                f"with the per device switching delay of "
                f"{SWITCHING_TOGGLE_DELAY_SECONDS} seconds.",
                status.HTTP_409_CONFLICT,
                f"Some switch requests were not executed in order to comply "
                f"with the per device switching delay of "
                f"{SWITCHING_TOGGLE_DELAY_SECONDS} seconds.",
            )

    def _try_switching_device(
        self, device: TreeItemDevice, desired_isOn: bool
    ) -> bool:
        """Function to request a device to switch. Ensures switching delays are
        respected.

        To comply with the inrush current delay the switching of the device is
        delayed.
        To comply with the individual switching delay of the device the device
        the switch request for this device will be discarded if the device
        would switch too early.

        @param device The device to switch.

        @param desired_isOn A boolean indicating if the item should be turned
        ON (True) or OFF (False).

        @return A boolean indicating if the request was dropped for this device
        (True) or not (False).
        """

        # TODO: remove, development code
        if USE_SWITCHING_DELAYS is False:
            SmartplugApp._mqtt_client.switch(device.deviceId, desired_isOn)
            return False

        with SmartplugApp._device_tree_mutex:

            if device.get_isOn() is desired_isOn:
                # The device is already in the desired state, no switching is
                # needed.
                return

            now = datetime.now()

            # Handle the inrush current delay (only needed if switching ON).
            if desired_isOn:
                with SmartplugApp._last_switch_on_date_time_mutex:

                    time_passed_since_last_switch_on: timedelta = (
                        now - SmartplugApp._last_switch_on_date_time
                    )

                    if (
                        time_passed_since_last_switch_on.seconds
                        < INRUSH_CURRENT_DELAY_SECONDS
                    ):

                        time.sleep(
                            INRUSH_CURRENT_DELAY_SECONDS
                            - time_passed_since_last_switch_on.seconds
                        )

                    SmartplugApp._last_switch_on_date_time = datetime.now()

            # Handle the individual switching delay of the device.
            now = datetime.now()
            time_passed_since_last_switch_of_current_item: timedelta = (
                now - device.time_last_switched
            )

            if time_passed_since_last_switch_of_current_item < timedelta(
                seconds=SWITCHING_TOGGLE_DELAY_SECONDS
            ):
                return True

            device.time_last_switched = now

        SmartplugApp._mqtt_client.switch(device.deviceId, desired_isOn)

        return False

    def _choose_devices_to_switch(
        self, tree_item: TreeItem, desired_isOn: bool
    ) -> list[TreeItemDevice]:
        """Function to choose devices to switch given a certain tree item an a
        desired state.

        If the tree item is a group this will colect all devices in that group.
        If switching a device would violate the device dependencies that device
        is skipped.

        @param tree_item The tree item to switch. May be a group or a device.

        @param desired_isOn A boolean indicating if the item should be turned
        ON (True) or OFF (False).

        @return The list of devices that should switch and are allowed to do
        so.
        """

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
