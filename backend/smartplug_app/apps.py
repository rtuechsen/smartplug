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
    _device_id_to_tree_item_mapping: dict[str, TreeItem] = {}

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
                lab_config_python_obj
            )

        # TODO: get values (isOn, ...) from devices

        # TODO: remove, used for debugging only
        random.seed(42)  # make the changes reproducible
        # set a (fixed) random initial state
        self.change_device_tree_randomly(
            len(SmartplugApp._device_id_to_tree_item_mapping.keys()) * 2
        )

    def _object_list_to_tree_item_list(
        self, object_list: list[dict]
    ) -> list[TreeItem]:
        """Converts a list of dictionaries (JSON) to a list of TreeItems.

        @param object_list A list of dictionaries representing tree items.

        @return A list of TreeItems.
        """

        # Note: passing a member function as a callback causes doxygen to think
        # it is a new attribute.
        # Seems to be a bug fixed in doxygen 1.13 but that is not available to
        # linux via apt.
        return list(map(self._object_to_tree_item, object_list))

    def _object_to_tree_item(self, obj: dict) -> TreeItem:
        """Converts a (hierarchy of) dictionary(s) (aka JSON) to a (hierarchy
        of) TreeItem(s).

        Verifies the structure of the data and provides feedback.

        @param obj A dictionary representing a tree item, possibly with more
        tree items as childrens.

        @return A TreeItem with possibly more TreeItems as its children.
        """

        # also verifies the correctness of the data, providing feedback to the
        # admin using error messages

        if "label" not in obj.keys():
            raise BackendError(f"Object {obj} is missing property 'label'.")

        if "turn_off_if_all_in_list_are_off" in obj.keys():
            if len(obj.keys()) != 3:
                raise BackendError(
                    f"Object {obj} has wrong amount of properties."
                )
        else:
            if len(obj.keys()) != 2:
                raise BackendError(
                    f"Object {obj} has wrong amount of properties."
                )

        if "deviceId" in obj.keys():
            if obj["deviceId"] in self._device_id_to_tree_item_mapping:
                raise BackendError(
                    f"Property 'deviceId' of {obj} is not unique."
                )
            tree_item = TreeItemDevice()
            tree_item.deviceId = obj["deviceId"]
            tree_item.isOn = False
            tree_item.isAvailable = False
            self._device_id_to_tree_item_mapping[tree_item.deviceId] = (
                tree_item
            )

        elif "children" in obj.keys():
            tree_item = TreeItemGroup()
            tree_item.children = self._object_list_to_tree_item_list(
                obj["children"]
            )
            if len(tree_item.children) == 0:
                self._logger.warn(f"Object {obj} is a group without children.")

        else:
            raise BackendError(
                f"Object {obj} is missing both 'deviceId' and 'children'."
            )

        tree_item.label = obj["label"]

        if "turn_off_if_all_in_list_are_off" in obj.keys():
            tree_item.turn_off_if_all_in_list_are_off = obj[
                "turn_off_if_all_in_list_are_off"
            ]
        else:
            tree_item.turn_off_if_all_in_list_are_off = None

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
                    tree_item.isAvailable = not tree_item.isAvailable
                else:
                    tree_item.isOn = not tree_item.isOn

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

    def switch(self, id: str, isOn: bool) -> None:
        """Function to answer a call to /switch, turns devices and groups
        on/off according to the request.

        @param id The id of the device or group to switch.

        @param isOn A boolean indicating if the item should be turned on (True)
        or off (False). Ignores PEP8 naming convention to match the name of the
        variable across the project.
        """

        # TODO: break function into smaller parts

        # if requests are dropped due to SWITCHING_TOGGLE_DELAY
        requests_dropped: bool = False

        def switch_recursive(id: str, isOn: bool):
            """A helper function that switches the item as well as all children
            in case the item is a group.

            @param id The id of the device or group to switch.

            @param isOn A boolean indicating if the item should be turned on
            (True) or off (False). Ignores PEP8 naming convention to match the
            name of the variable across the project.
            """

            if id not in SmartplugApp._id_to_tree_item_mapping:

                raise BackendError(
                    f"Specified id {id} does not exist.",
                    status.HTTP_400_BAD_REQUEST,
                    "Specified id does not exist.",
                )

            tree_item = SmartplugApp._id_to_tree_item_mapping[id]

            if isinstance(tree_item, TreeItemDevice):

                with SmartplugApp._device_tree_mutex:

                    if tree_item.isOn == isOn:
                        # isOn is already in desired state, no switching needed
                        return

                    now = datetime.datetime.now()

                    # TODO: need to save last 'switch ON time' (mutex), wait if
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
                    ) = (now - tree_item.time_last_switched)

                    if (
                        time_passed_since_last_switch_of_current_item
                        < datetime.timedelta(seconds=SWITCHING_TOGGLE_DELAY)
                    ):

                        # need to declare variable as 'nonlocal' to avoid 
                        # redefining it
                        nonlocal requests_dropped
                        requests_dropped = True

                        # if last switch request was not that long ago -> drop 
                        # this request
                        return

                    tree_item.time_last_switched = now

                    # TODO: try sending MQTT request here !!!

                    # TODO: do NOT set state here / send update event here, 
                    # wait for signal from plug that it changed somewhere else 
                    # in the code
                    tree_item.isOn = isOn

                # notify SSE subscribers about changes to the device tree
                django_eventstream.send_event(
                    "device_tree_update",
                    "message",
                    self.get_device_tree_dicts(),
                )
                print(f"executed switch for device: {tree_item.label}")

            elif isinstance(tree_item, TreeItemGroup):
                for child in tree_item.children:
                    switch_recursive(child.id, isOn)
            else:
                raise BackendError(
                    f"Implementation error, 'tree_item' {tree_item} is of "
                    f"unknown class: {type(tree_item)}."
                )

        # TODO: remove, simulating latency
        # time.sleep(1)

        switch_recursive(id, isOn)

        # TODO: add info about delay value
        if requests_dropped:
            raise BackendError(
                f"Some switch requests were not executed in order to comply "
                f"with the per device switching delay of "
                f"{SWITCHING_TOGGLE_DELAY} seconds.",
                status.HTTP_409_CONFLICT,
                f"Some switch requests were not executed in order to comply "
                f"with the per device switching delay of "
                f"{SWITCHING_TOGGLE_DELAY} seconds.",
            )

    def _solve_item_dependencies(self):

        ids_to_switch_off: list[str] = []

        def solve_recursive(id: str):

            tree_item = SmartplugApp._id_to_tree_item_mapping[id]

            if tree_item.turn_off_if_all_in_list_are_off is not None:

                # TODO: check status of all device_ids
                all_devices_are_off = True
                for deviceId in tree_item.turn_off_if_all_in_list_are_off:
                    tree_item_dep: TreeItemDevice = (
                        SmartplugApp._device_id_to_tree_item_mapping[deviceId]
                    )
                    if (
                        tree_item_dep.isOn
                        and tree_item_dep.id not in ids_to_switch_off
                    ):
                        all_devices_are_off = False
                        break

                if all_devices_are_off:
                    ids_to_switch_off.append(tree_item.id)
                # TODO: problem: need to do this again and again, because 
                # turning something off could trigger another dependency

            if isinstance(tree_item, TreeItemGroup):
                for child in tree_item.children:
                    solve_recursive(child.id)
            else:
                raise BackendError(
                    f"Implementation error, 'tree_item' {tree_item} is of "
                    f"unknown class: {type(tree_item)}."
                )

        with SmartplugApp._device_tree_mutex:
            for item in SmartplugApp._device_tree:
                solve_recursive(item.id)

        for id in ids_to_switch_off:
            SmartplugApp.switch(self, id, False)

    def _build_dependency_tree(self):

        # deviceId -> list[deviceId]
        # if_I_turn_off -> those_might_turn_off
        # e.g. PC1 -> [Monitor1, Monitor2]
        dependencies: dict = {}

        def collect_dependencies(id: str, add_to_all_children: list[str]):

            tree_item = SmartplugApp._id_to_tree_item_mapping[id]

            if tree_item.turn_off_if_all_in_list_are_off is not None:

                add_to_all_children = (
                    add_to_all_children
                    + tree_item.turn_off_if_all_in_list_are_off
                )

            if isinstance(tree_item, TreeItemDevice):

                for deviceId in add_to_all_children:
                    if deviceId in dependencies:
                        dependencies[deviceId].append(tree_item.deviceId)
                    else:
                        dependencies[deviceId] = [tree_item.deviceId]

            elif isinstance(tree_item, TreeItemGroup):
                for child in tree_item.children:
                    collect_dependencies(child.id, add_to_all_children)
            else:
                raise BackendError(
                    f"Implementation error, 'tree_item' {tree_item} is of "
                    f"unknown class: {type(tree_item)}."
                )

        with SmartplugApp._device_tree_mutex:
            for item in SmartplugApp._device_tree:
                collect_dependencies(item.id, [])

        another_dep_was_found = True
        while another_dep_was_found:
            another_dep_was_found = False

            # go over all deps:
            # if dep is referenced in another dep:

            # TODO: add dependencies of dependencies, detect circular 
            # dependencies

        # TODO: check dependencies during switching
