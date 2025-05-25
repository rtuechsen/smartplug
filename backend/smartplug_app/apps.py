"""Contains the SmartplugApp class which stores most of the data for the
backend and also handles background tasks the REST API does not handle.

TODO: more details ???
"""

# TODO: we need a tool to wrap comments and docstrings to the maximum line
# lenght of PEP8, black formatter does not handle those

import json
import random
import hashlib
import threading
from pathlib import Path
from django.apps import AppConfig
from rest_framework import status
from .error_handler import BackendError
from .logger import Logger
from .tree_item import TreeItem, TreeItemDevice, TreeItemGroup


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

    def ready(self) -> None:

        SmartplugApp._logger.info("Server was started.")

        # load the config.json
        self._load_config()

    def _load_config(self) -> list[TreeItemDevice | TreeItemGroup]:
        """Loads the hierarchy of devices and groups from `config.json`.

        The file 'config.json' is expected to be located in the root
        directory of this project.

        @return The hierarchy of devices and groups.
        """

        # 1. read the config.json file

        config_file_path: str = "./config.json"

        lab_config_path = (
            Path(__file__).parent.parent.parent / config_file_path
        )

        try:
            with open(lab_config_path, "r", encoding="utf8") as file:
                lab_config_json_string = file.read()
        except FileNotFoundError:
            self._logger.error(
                f"Could not find the file config.json at {lab_config_path}."
            )
        except IOError:
            self._logger.error(
                f"Error while reading the file config.json at "
                f"{lab_config_path}."
            )

        # 2. convert string from file to JSON (dicts and lists)

        try:
            lab_config_python_obj = json.loads(lab_config_json_string)
        except ValueError as e:
            self._logger.error(
                "Could not parse config.json to JSON because "
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

        if len(obj.keys()) != 2:
            raise BackendError(f"Object {obj} has not exactly two properties.")
        if "label" not in obj.keys():
            raise BackendError(f"Object {obj} is missing property 'label'.")

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

    def switch(self, id: str, desired_isOn: bool) -> None:
        """Function to answer a call to /switch, turns devices and groups
        on/off according to the request.

        @param id The id of the device or group to switch.

        @param desired_isOn A boolean indicating if the item should be turned
        on (True) or off (False). Ignores PEP8 naming convention to match the
        name of the variable across the project.
        """

        def switch_recursive(id: str, desired_isOn: bool):
            """A helper function that switches the item as well as all children
            in case the item is a group.

            @param id The id of the device or group to switch.

            @param desired_isOn A boolean indicating if the item should be
            turned on (True) or off (False). Ignores PEP8 naming convention to
            match the name of the variable across the project.
            """

            if id not in SmartplugApp._id_to_tree_item_mapping:

                raise BackendError(
                    f"Specified id {id} does not exist.",
                    status.HTTP_400_BAD_REQUEST,
                    "Specified id does not exist.",
                )

            tree_item = SmartplugApp._id_to_tree_item_mapping[id]

            if isinstance(tree_item, TreeItemDevice):
                # TODO: actually (try to) switch the plug here
                tree_item.isOn = desired_isOn
            elif isinstance(tree_item, TreeItemGroup):
                for child in tree_item.children:
                    switch_recursive(child.id, desired_isOn)
            else:
                raise BackendError(
                    f"Implementation error, 'tree_item' {tree_item} is of "
                    f"unknown class: {type(tree_item)}."
                )

        with SmartplugApp._device_tree_mutex:
            switch_recursive(id, desired_isOn)

        # notify SSE subscribers about changes to the device tree
        send_event(
            "default",
            "device_tree_update",
            self.get_device_tree_dicts(),
        )
