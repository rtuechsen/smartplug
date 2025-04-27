import threading
import time
import json
import random
import hashlib
import warnings
from pathlib import Path
from django.apps import AppConfig
from django_eventstream import send_event
from rest_framework import status
from .ErrorHandler import BackendError
from .TreeItem import TreeItem, TreeItemDevice, TreeItemGroup


# TODO: better name for class
class InternalApp(AppConfig):

    # TODO: consider renaming as well
    name: str = "shelly_dirigent"

    # needed to avoid starting background task multiple times
    background_task_started: bool = False

    # main data structure to hold the data of the devices and groups
    device_tree: list[TreeItemDevice | TreeItemGroup]

    # mutex to avoid race conditions on the device tree
    device_tree_mutex = threading.Lock()

    # mapping to get the TreeItem for a given id
    id_to_tree_item_mapping: dict[str, TreeItem] = {}

    # mapping to get the TreeItem for a given deviceId
    device_id_to_tree_item_mapping: dict[str, TreeItem] = {}

    def ready(self):
        print("\n\n -> Starting internal app ...\n\n")

        # TODO: log server start

        # load the labor-config.json
        self.load_labor_config()

        if not self.background_task_started:
            self.background_task_started = True
            thread = threading.Thread(target=self.loop, daemon=True)
            thread.start()

    # TODO: remove, used for debugging only
    def loop(self) -> None:
        time.sleep(2)
        while True:
            time.sleep(4)
            print("\n\n -> Running background task ...\n\n")
            # TODO: remove, used for debugging only
            # self.change_device_tree_randomly(10)
            send_event("device_tree_update", "message", self.get_device_tree_dicts())

    def load_labor_config(self) -> list[TreeItemDevice | TreeItemGroup]:

        # 1. read the file

        labor_config_file_path: str = "./labor-config.json"

        lab_config_path = Path(__file__).parent.parent.parent / labor_config_file_path

        try:
            with open(lab_config_path, "r", encoding="utf8") as file:
                lab_config_json_string = file.read()
        except FileNotFoundError:
            print(f"Error: Could not find the file {lab_config_path}")
        except IOError:
            print(f"Error: while reading the file {lab_config_path}")

        # 2. convert to JSON (dicts and lists)

        try:
            lab_config_python_obj = json.loads(lab_config_json_string)
        except ValueError as e:
            print(f"Error: Could not parse JSON {lab_config_json_string} because {e}")

        # 3. convert to classes

        with self.device_tree_mutex:
            self.device_tree = self.object_list_to_tree_item_list(lab_config_python_obj)

        # TODO: get values (isOn, ...) from devices

        # TODO: remove, used for debugging only
        random.seed(42)  # make the changes reproducible
        # set a (fixed) random initial state
        self.change_device_tree_randomly(
            len(self.device_id_to_tree_item_mapping.keys()) * 2
        )

    def object_list_to_tree_item_list(self, object_list: list[dict]) -> list[TreeItem]:
        """Converts a list of dictionaries (JSON) to a list of TreeItems"""

        return list(map(self.object_to_tree_item, object_list))

    def object_to_tree_item(self, obj: dict) -> TreeItem:
        """Converts a (hierarchy of) dictionary (JSON) to a (hierarchy of) TreeItem"""

        # also verifies the correctness of the data, providing feedback to the admin using error messages

        if len(obj.keys()) != 2:
            raise RuntimeError(f"Error: object {obj} has not exactly two keys!")
        if "label" not in obj.keys():
            raise RuntimeError(f"Error: object {obj} is missing 'label'!")

        if "deviceId" in obj.keys():
            if obj["deviceId"] in self.device_id_to_tree_item_mapping:
                raise RuntimeError(f"Error: deviceId of {obj} is not unique!")
            tree_item = TreeItemDevice()
            tree_item.deviceId = obj["deviceId"]
            tree_item.isOn = False
            tree_item.isAvailable = False
            self.device_id_to_tree_item_mapping[tree_item.deviceId] = tree_item

        elif "children" in obj.keys():
            tree_item = TreeItemGroup()
            tree_item.children = self.object_list_to_tree_item_list(obj["children"])
            if len(tree_item.children) == 0:
                warnings.warn(f"Warning: object {obj} is a group without children!")

        else:
            raise RuntimeError(
                f"Error: object {obj} is missing both 'deviceId' and 'children'!"
            )

        tree_item.label = obj["label"]

        # use (cryptographic) hash of label for id in order to keep the same id across runs
        # this hides the deviceId of the shelly plugs from the clients and gives ids to groups as well
        hash_source: str = tree_item.label
        tree_item.id = hashlib.sha256(str.encode(hash_source)).hexdigest()
        while tree_item.id in self.id_to_tree_item_mapping:
            # if the label is not unique in the file change the hash source (deterministically) until a unique hash is created
            hash_source += "0"
            tree_item.id = hashlib.sha256(str.encode(hash_source)).hexdigest()

        self.id_to_tree_item_mapping[tree_item.id] = tree_item

        return tree_item

    # TODO: remove, used for debugging only
    def change_device_tree_randomly(self, number_of_changes=1) -> None:

        for _ in range(number_of_changes):

            device_id: str = random.choice(
                list(self.device_id_to_tree_item_mapping.keys())
            )
            tree_item: TreeItemDevice = self.device_id_to_tree_item_mapping[device_id]

            toggle_availability: bool = random.choice([True, False])

            with self.device_tree_mutex:

                if toggle_availability:
                    tree_item.isAvailable = not tree_item.isAvailable
                else:
                    tree_item.isOn = not tree_item.isOn

    def get_device_tree_dicts(self) -> list[dict]:
        """Function to answer a call to /gettree, returns the current state of the tree."""

        device_tree_dict: list[dict] = []

        # TODO: remove, simulating latency
        # time.sleep(2)

        # always lock the tree before working on it
        with self.device_tree_mutex:
            for tree_item in self.device_tree:
                tree_item_dict = tree_item.to_dict()
                device_tree_dict.append(tree_item_dict)

        return device_tree_dict

    def switch(self, id: str, isOn: bool) -> None:
        """Function to answer a call to /switch, turns groups and devices on/off according to the request."""

        def switch_recursive(id: str, isOn: bool):

            if id not in self.id_to_tree_item_mapping:
                # this error will automatically be propagated back as a proper response to the requesting client

                raise BackendError(
                    f"Specified id {id} does not exist.",
                    status.HTTP_400_BAD_REQUEST,
                    "Specified id does not exist.",
                )

            tree_item = self.id_to_tree_item_mapping[id]

            if isinstance(tree_item, TreeItemDevice):
                # TODO: actually (try to) switch the plug here
                tree_item.isOn = isOn
            elif isinstance(tree_item, TreeItemGroup):
                for child in tree_item.children:
                    switch_recursive(child.id, isOn)
            else:
                raise BackendError(
                    f"Implementation error, 'tree_item' {tree_item} is of unknown class: {type(tree_item)}."
                )

        # TODO: remove, simulating latency
        time.sleep(1)

        with self.device_tree_mutex:
            switch_recursive(id, isOn)

        # notify SSE subscribers about changes to the device tree
        send_event("device_tree_update", "message", self.get_device_tree_dicts())
