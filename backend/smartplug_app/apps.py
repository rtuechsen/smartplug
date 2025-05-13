"""Contains the TODO class which stores most of the data for the backend and
also handles background tasks the REST API does not handle.

TODO: more details ???
"""

# TODO: we need a tool to wrap comments and docstrings to the maximum line
# lenght of PEP8, black formatter does not handle those

import time
import json
import random
import hashlib
import threading
from pathlib import Path
import datetime
from django.apps import AppConfig
import django_eventstream
from rest_framework import status
from .error_handler import BackendError
from .logger import Logger
from .tree_item import TreeItem, TreeItemDevice, TreeItemGroup
from .admin_settings import SWITCHING_TOGGLE_DELAY, INRUSH_CURRENT_DELAY


class SmartplugApp(AppConfig):
    """The main class for storing data about devices and groups as well as
    their state. Also handles background tasks the REST API does not handle.

    This module is registered in the django settings as an app. This
    means it is instanciated by django when the server starts.

    It reads labor-config.json and holds the hierarchy of devices and
    groups as well as their current state. It is used by the REST API to
    get or manipulate data from the device hierarchy. It holds the mqtt
    client to communicate with the devices.

    Functions that answer calls from the REST API should raise
    BackendError's. Other function might do this as well if it makes
    sense.

    Apps in Django usually define and initialize all their attributes as
    class attributes. When Django has loaded all models the
    ready()-function of all apps are called.
    """

    ## The name of the app (required by Django).
    name: str = "smartplug_app"

    ## Boolean needed to avoid starting background task multiple times.
    _background_task_started: bool = False

    ## The main data structure to hold the hierarchy of devices and groups and
    ## their current state.
    _device_tree: list[TreeItemDevice | TreeItemGroup]

    ## A mutex to avoid race conditions on the device tree. Needed because
    ## async calls from the REST API are possible. ALWAYS lock this mutex when
    ## reading or manipulating the device tree!
    _device_tree_mutex: threading.Lock = threading.Lock()

    ## A mapping to get the TreeItem for a given id.
    _id_to_tree_item_mapping: dict[str, TreeItem] = {}

    ## A mapping to get the TreeItem for a given deviceId.
    _device_id_to_tree_item_mapping: dict[str, TreeItemDevice] = {}

    ## The logger instance (singleton) to log events and errors.
    _logger: Logger = Logger()

    _last_switch_on_date_time: datetime.datetime = datetime.datetime.now()

    _last_switch_on_date_time_mutex: threading.Lock = threading.Lock()

    def ready(self) -> None:

        SmartplugApp._logger.info("Server was started.")

        # load the labor-config.json
        self._load_labor_config()

        # TODO: remove, used for debugging only
        # if not SmartplugApp._background_task_started:
        #     SmartplugApp._background_task_started = True
        #     thread = threading.Thread(target=self.loop, daemon=True)
        #     thread.start()

    # TODO: remove, used for debugging only
    def loop(self) -> None:
        time.sleep(2)
        while True:
            time.sleep(4)
            print("\n\n -> Running background task ...\n\n")
            # TODO: remove, used for debugging only
            # self.change_device_tree_randomly(10)
            django_eventstream.send_event(
                "device_tree_update", "message", self.get_device_tree_dicts()
            )

    def _load_labor_config(self) -> list[TreeItemDevice | TreeItemGroup]:
        """Loads the hierarchy of devices and groups from `labor-config.json`.

        The file 'labor-config.json' is expected to be located in the root
        directory of this project.

        @return The hierarchy of devices and groups.
        """

        # 1. read the labor-config.json file

        labor_config_file_path: str = "./labor-config.json"

        lab_config_path = (
            Path(__file__).parent.parent.parent / labor_config_file_path
        )

        try:
            with open(lab_config_path, "r", encoding="utf8") as file:
                lab_config_json_string = file.read()
        except FileNotFoundError:
            self._logger.error(
                f"Could not find the file labor-config at {lab_config_path}."
            )
        except IOError:
            self._logger.error(
                f"Error while reading the file labor-config at "
                f"{lab_config_path}."
            )

        # 2. convert string from file to JSON (dicts and lists)

        try:
            lab_config_python_obj = json.loads(lab_config_json_string)
        except ValueError as e:
            self._logger.error(
                "Could not parse the labor-config to JSON because "
                f"{e}: {lab_config_json_string}."
            )

        # 3. convert to classes

        with SmartplugApp._device_tree_mutex:
            # errors from parsing will not be logged but will result in an
            # unhandled exception immediately after starting the server
            SmartplugApp._device_tree = self._object_list_to_tree_item_list(
                lab_config_python_obj, None, []
            )
            self._collect_dependencies()

        # TODO: get values (isOn, ...) from devices

        # TODO: remove, used for debugging only
        random.seed(42)  # make the changes reproducible
        # set a (fixed) random initial state
        self.change_device_tree_randomly(
            len(SmartplugApp._device_id_to_tree_item_mapping.keys()) * 2
        )

    def _object_list_to_tree_item_list(
        self,
        object_list: list[dict],
        parent: TreeItemGroup,
        turn_off_if_all_in_list_are_off: list[TreeItemDevice],
    ) -> list[TreeItem]:
        """Converts a list of dictionaries (JSON) to a list of TreeItems.

        TODO: warning: does not use mutex

        @param object_list A list of dictionaries representing tree items.

        @return A list of TreeItems.
        """

        if not isinstance(object_list, list):
            raise BackendError(
                f"Object {object_list} should be a list, but isn't."
            )

        # Note: passing a member function as a callback causes doxygen to think
        # it is a new attribute.
        # Seems to be a bug fixed in doxygen 1.13 but that is not available to
        # linux via apt.
        return list(
            map(
                lambda obj_list: self._object_to_tree_item(
                    obj_list, parent, turn_off_if_all_in_list_are_off
                ),
                object_list,
            )
        )

    def _object_to_tree_item(
        self,
        obj: dict,
        parent: TreeItemGroup,
        turn_off_if_all_in_list_are_off: list[TreeItemDevice],
    ) -> TreeItem:
        """Converts a (hierarchy of) dictionary(s) (aka JSON) to a (hierarchy
        of) TreeItem(s).

        Verifies the structure of the data and provides feedback.

        TODO: warning: does not use mutex

        @param obj A dictionary representing a tree item, possibly with more
        tree items as childrens.

        @return A TreeItem with possibly more TreeItems as its children.
        """

        # also verifies the correctness of the data, providing feedback to the
        # admin using error messages

        if "label" not in obj:
            raise BackendError(f"Object {obj} is missing property 'label'.")

        if "turn_off_if_all_in_list_are_off" in obj:
            if len(obj.keys()) != 3:
                raise BackendError(
                    f"Object {obj} has wrong amount of properties."
                )
        else:
            if len(obj.keys()) != 2:
                raise BackendError(
                    f"Object {obj} has wrong amount of properties."
                )

        if "deviceId" in obj:
            if obj["deviceId"] in self._device_id_to_tree_item_mapping:
                raise BackendError(
                    f"Property 'deviceId' of {obj} is not unique."
                )
            tree_item = TreeItemDevice()
            tree_item.deviceId = obj["deviceId"]
            if "turn_off_if_all_in_list_are_off" in obj:
                tree_item.turn_off_if_all_in_list_are_off = obj[
                    "turn_off_if_all_in_list_are_off"
                ]
            else:
                tree_item.turn_off_if_all_in_list_are_off = []
            self._device_id_to_tree_item_mapping[tree_item.deviceId] = (
                tree_item
            )

        elif "children" in obj:
            tree_item = TreeItemGroup()
            if "turn_off_if_all_in_list_are_off" in obj:
                turn_off_if_all_in_list_are_off.extend(
                    obj["turn_off_if_all_in_list_are_off"]
                )
            tree_item.children = self._object_list_to_tree_item_list(
                obj["children"], tree_item, turn_off_if_all_in_list_are_off
            )
            if len(tree_item.children) == 0:
                self._logger.warn(f"Object {obj} is a group without children.")

        else:
            raise BackendError(
                f"Object {obj} is missing both 'deviceId' and 'children'."
            )

        tree_item.label = obj["label"]
        tree_item.parent = parent

        # Use (cryptographic) hash of the items label for the id in order to
        # keep the same id across runs.
        # This hides the deviceId of the smartplugs from the clients and gives
        # ids to groups as well.
        hash_source: str = tree_item.label
        tree_item.id = hashlib.sha256(str.encode(hash_source)).hexdigest()
        while tree_item.id in SmartplugApp._id_to_tree_item_mapping:
            # if the label is not unique in the file change the hash source
            # (deterministically) until a unique hash is created
            hash_source += "0"
            tree_item.id = hashlib.sha256(str.encode(hash_source)).hexdigest()

        SmartplugApp._id_to_tree_item_mapping[tree_item.id] = tree_item

        return tree_item

    # TODO: remove, used for debugging only
    def change_device_tree_randomly(self, number_of_changes=1) -> None:

        for _ in range(number_of_changes):

            device_id: str = random.choice(
                list(self._device_id_to_tree_item_mapping.keys())
            )
            tree_item: TreeItemDevice = (
                SmartplugApp._device_id_to_tree_item_mapping[device_id]
            )

            toggle_availability: bool = random.choice([True, False])

            with SmartplugApp._device_tree_mutex:

                if toggle_availability:
                    tree_item.set_isAvailable(not tree_item.get_isAvailable())
                else:
                    tree_item.set_isOn(not tree_item.get_isOn())

    def get_device_tree_dicts(self) -> list[dict]:
        """Function to answer a call to /gettree, returns the current state of
        the tree.

        @return A hierarchy of dictionaries and lists representing the current
        state of the device tree.
        """

        device_tree_dict: list[dict] = []

        # TODO: remove, simulating latency
        # time.sleep(2)

        # always lock the tree before working on it
        with SmartplugApp._device_tree_mutex:
            for tree_item in SmartplugApp._device_tree:
                tree_item_dict = tree_item.to_dict()
                device_tree_dict.append(tree_item_dict)

        return device_tree_dict

    def on_device_switch(self, deviceId: str, isOn: bool) -> None:

        # TODO: validate deviceId does exist
        device = SmartplugApp._device_id_to_tree_item_mapping[deviceId]

        device.set_isOn(isOn)

        if device.get_isOn() is True:
            return

        # only do single dependency step! further deps will be handled once their isOn state has been confirmed

        for (
            listener_device
        ) in device.other_devices_listening_for_this_device_switching_off:

            if listener_device.get_isOn() is False:
                # already off, no action needed
                continue

            # listener_device is ON, need to check its dependencies to see if should be turned OFF after change

            trigger_states = [
                trigger_device.get_isOn()
                for trigger_device in listener_device.turn_off_if_all_in_list_are_off
            ]

            if all(not state for state in trigger_states):
                SmartplugApp.switch(self, listener_device.id, False)

    def _filter_devices_not_allowed_to_switch_on(
        self,
        devices_to_switch: list[TreeItemDevice],
    ):

        # re-evaluating tree should not be necessary while resolving deps (because devices cannot depend on groups)

        resolved_states: dict[str, bool] = {}

        # only need to make sure that all the devices are allowed to switch, e.g. not switching monitor on without PC on

        # traverse deps backwards: first leaves with no own deps, then their listeners

        # returns the new state a device
        def will_be_on(device: TreeItemDevice):

            # check if device has already been checked, return that value in that case
            if device.deviceId in resolved_states:
                return resolved_states[device.deviceId]

            if device.get_isOn() is True:
                resolved_states[device.deviceId] = True
                return True

            # device is OFF -> only way it might be ON afterwards if it is amoung devices_to_switch
            if device not in devices_to_switch:
                resolved_states[device.deviceId] = False
                return False

            # device is OFF, but is scheduled to be switched ON -> can still fail if all dependencies are off

            trigger_states: list[bool] = [
                will_be_on(trigger_device)
                for trigger_device in device.turn_off_if_all_in_list_are_off
            ]

            if all(not state for state in trigger_states):
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

    def switch(self, id: str, isOn: bool) -> None:
        """Function to answer a call to /switch, turns devices and groups
        on/off according to the request.

        @param id The id of the device or group to switch.

        @param isOn A boolean indicating if the item should be turned on (True)
        or off (False). Ignores PEP8 naming convention to match the name of the
        variable across the project.
        """

        # TODO: break function into smaller parts

        if id not in SmartplugApp._id_to_tree_item_mapping:

            raise BackendError(
                f"Specified id {id} does not exist.",
                status.HTTP_400_BAD_REQUEST,
                "Specified id does not exist.",
            )

        def choose_devices_to_switch(
            id: str, isOn: bool
        ) -> list[TreeItemDevice]:

            def get_devices(tree_item: TreeItem):

                if isinstance(tree_item, TreeItemDevice):
                    return [tree_item]

                elif isinstance(tree_item, TreeItemGroup):
                    devices = []
                    for child in tree_item.children:
                        devices.extend(get_devices(child))
                    return devices

            tree_item = SmartplugApp._id_to_tree_item_mapping[id]
            all_devices: list[TreeItemDevice] = get_devices(tree_item)
            devices_to_switch: list[TreeItemDevice] = [
                device
                for device in all_devices
                if device.get_isOn() is not isOn
            ]

            if isOn is True:
                devices_to_switch: list[TreeItemDevice] = (
                    self._filter_devices_not_allowed_to_switch_on(
                        devices_to_switch
                    )
                )

            return devices_to_switch

        devices_to_switch: list[TreeItemDevice] = choose_devices_to_switch(
            id, isOn
        )

        # if requests are dropped due to SWITCHING_TOGGLE_DELAY
        were_requests_dropped: bool = False

        for device in devices_to_switch:

            with SmartplugApp._device_tree_mutex:

                if device.get_isOn() is isOn:
                    # isOn is already in desired state, no switching needed
                    return

                now = datetime.datetime.now()

                # need to save last 'switch ON time' (mutex), wait if
                # below delay
                # TODO: only delay between device switches, not at
                # beginning or end of request
                if isOn:
                    # only delay switching when switching ON (no inrush
                    # current when switching OFF)
                    with SmartplugApp._last_switch_on_date_time_mutex:

                        time_passed_since_last_switch_on: (
                            datetime.timedelta
                        ) = (now - SmartplugApp._last_switch_on_date_time)

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
                    were_requests_dropped = True

                    # if last switch request was not that long ago -> drop
                    # this request
                    return

                device.time_last_switched = now

                # TODO: try sending MQTT request here !!!

                # TODO: do NOT set state here,
                # wait for signal from plug that it changed somewhere else
                # in the code
                device.set_isOn(isOn)

            # TODO: do NOT send update event here,
            # wait for signal from plug that it changed somewhere else
            # in the code
            # notify SSE subscribers about changes to the device tree
            django_eventstream.send_event(
                "device_tree_update",
                "message",
                self.get_device_tree_dicts(),
            )

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

    def _collect_dependencies(self):
        """

        TODO: warning: does not use mutex

        """

        # TODO: detect cyclic dependencies

        # TODO: do NOT re-use variable with different type !!!
        # store deviceIds in dictionary during parsing (local variable in load())
        def convert_ids_to_references(tree_item: TreeItem):

            for device_index, deviceId in enumerate(
                tree_item.turn_off_if_all_in_list_are_off
            ):

                # TODO: verify that deviceId exists

                tree_item.turn_off_if_all_in_list_are_off[device_index] = (
                    SmartplugApp._device_id_to_tree_item_mapping[deviceId]
                )

            if isinstance(tree_item, TreeItemGroup):
                for child_item in tree_item.children:
                    convert_ids_to_references(child_item)

        for item in SmartplugApp._device_tree:
            convert_ids_to_references(item)

        def collect_dependencies_recursive(
            item: TreeItemDevice | TreeItemGroup,
        ):

            if isinstance(item, TreeItemDevice):
                for dependency_item in item.turn_off_if_all_in_list_are_off:

                    dependency_item.other_devices_listening_for_this_device_switching_off.append(
                        item
                    )

            elif isinstance(item, TreeItemGroup):
                for child in item.children:
                    collect_dependencies_recursive(child)

        for item in SmartplugApp._device_tree:
            collect_dependencies_recursive(item)
