import json
import hashlib
from pathlib import Path
import networkx
from .logger import Logger
from .tree_item import TreeItem, TreeItemGroup, TreeItemDevice
from .error_handler import BackendError


class DeviceTree:

    def __init__(self, file_path_rel: Path):

        ## The logger instance (singleton) to log events and errors.
        self._logger: Logger = Logger()

        ## The main data structure to hold the hierarchy of devices and groups
        ## and their current state.
        self._tree: list[TreeItemDevice | TreeItemGroup] = []

        ## A mapping to get the TreeItem for a given id.
        self._id_to_tree_item_mapping: dict[str, TreeItem] = {}

        ## A mapping to get the TreeItem for a given deviceId.
        self._deviceId_to_device_mapping: dict[str, TreeItemDevice] = {}

        self._load(file_path_rel)

    def _load(self, file_path_rel: Path) -> None:
        """Loads the hierarchy of devices and groups from `config.json`.

        The file 'config.json' is expected to be located in the root
        directory of this project.

        @return The hierarchy of devices and groups.
        """

        # 1. read the config.json file

        file_path_rel: str = "./config.json"

        file_path_abs = Path(__file__).parent.parent.parent / file_path_rel

        try:
            with open(file_path_abs, "r", encoding="utf8") as file:
                config_json_string = file.read()
        except FileNotFoundError as e:
            raise BackendError(
                f"Could not find the file config.json at {file_path_abs}."
            ) from e
        except IOError as e:
            raise BackendError(
                f"Error while reading the file config.json at "
                f"{file_path_abs}."
            ) from e

        # 2. convert string from file to JSON (dicts and lists)

        try:
            config_obj: list = json.loads(config_json_string)
        except ValueError as e:
            raise BackendError(
                f"Failed to parse config.json to JSON: "
                f"{e}: {config_json_string}."
            ) from e

        if not isinstance(config_obj, dict):
            raise BackendError(
                f"Expected a single JSON object at the highest level, but "
                f"found {type(config_obj)}"
            ) from e

        if len(config_obj) != 2:
            raise BackendError(
                f"Object {config_obj} has wrong amount of properties, should "
                f"be ['devices', 'tree']."
            )

        if "devices" not in config_obj:
            raise BackendError(
                f"Object {config_obj} is missing property 'devices'."
            )

        if "tree" not in config_obj:
            raise BackendError(
                f"Object {config_obj} is missing property 'tree'."
            )

        device_objs: list[dict] = config_obj.get("devices")
        tree_obj: list[dict] = config_obj.get("tree")

        # 3. convert to classes

        for device_obj in device_objs:
            device: TreeItemDevice = self._parse_device(device_obj)

            if device.deviceId in self._deviceId_to_device_mapping:
                self._logger.error(
                    f"The 'deviceId' of device {device_obj} is not unique."
                )

            self._deviceId_to_device_mapping[device.deviceId] = device

        self._tree = self._object_to_tree_item(tree_obj, None)

        for device in self._deviceId_to_device_mapping.values():
            if len(device.parents) == 0:
                self._logger.warn(
                    f"Device with deviceId {device.deviceId} is defined but "
                    "not used in the tree."
                )

        self._collect_dependencies(device_objs)

    def _parse_device(self, device_obj: dict) -> TreeItemDevice:

        if "label" not in device_obj:
            raise BackendError(
                f"Device {device_obj} is missing property 'label'."
            )

        if not isinstance(device_obj.get("label"), str):
            raise BackendError(
                f"Property 'label' in device {device_obj} has wrong type "
                f"{type(device_obj.get('label'))}, expcted: str."
            )

        if "deviceId" not in device_obj:
            raise BackendError(
                f"Device {device_obj} is missing property 'deviceId'."
            )

        if not isinstance(device_obj.get("deviceId"), str):
            raise BackendError(
                f"Property 'deviceId' in device {device_obj} has wrong type "
                f"{type(device_obj.get('deviceId'))}, expcted: str."
            )

        if "turn_off_if_all_in_list_are_off" in device_obj:
            if len(device_obj) != 3:
                raise BackendError(
                    f"Device {device_obj} has wrong amount of properties, "
                    f"expected "
                    f"['label','deviceId','turn_off_if_all_in_list_are_off']."
                )
            if not isinstance(
                device_obj.get("turn_off_if_all_in_list_are_off"), list
            ):
                raise BackendError(
                    f"Property 'turn_off_if_all_in_list_are_off' in device "
                    f"{device_obj} has wrong type "
                    f"{type(device_obj.get('turn_off_if_all_in_list_are_off'))}"
                    ", expcted: list[str]."
                )
            for deviceId in device_obj.get("turn_off_if_all_in_list_are_off"):
                if not isinstance(deviceId, str):
                    raise BackendError(
                        f"An item in property 'turn_off_if_all_in_list_are_off'"
                        f" in device {device_obj} has wrong type {type(deviceId)}"
                        f", expcted: str."
                    )
        else:
            if len(device_obj) != 2:
                raise BackendError(
                    f"Device {device_obj} has wrong amount of properties, "
                    f"expected ['label','deviceId']."
                )

        device = TreeItemDevice()
        device.label = device_obj.get("label")
        device.deviceId = device_obj.get("deviceId")

        return device

    def _object_list_to_tree_item_list(
        self,
        object_list: list[dict],
        parent: TreeItemGroup,
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

        return list(
            map(
                lambda obj_list: self._object_to_tree_item(obj_list, parent),
                object_list,
            )
        )

    def _object_to_tree_item(
        self,
        obj: dict,
        parent: TreeItemGroup,
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

        if not isinstance(obj, dict):
            raise BackendError(
                f"Object {obj} should be a dictionary, but is of type "
                f"{type(obj)}."
            )

        # ---------------------------------------------------------------------

        if "deviceId" in obj:

            if len(obj) != 1:
                raise BackendError(
                    f"Device reference {obj} has wrong amount of properties, "
                    f"expected ['deviceId']."
                )

            if not isinstance(obj.get("deviceId"), str):
                raise BackendError(
                    f"Property 'deviceId' in device {obj} has wrong type "
                    f"{type(obj.get('deviceId'))}, expcted: str."
                )

            device = self._deviceId_to_device_mapping.get(obj.get("deviceId"))

            if device is None:
                raise BackendError(
                    f"Object refers to a 'deviceId' that does not exist: "
                    f"{obj.get("deviceId")}."
                )

            device.parents.append(parent)
            self._add_unique_id(device, parent)
            return device

        # ---------------------------------------------------------------------

        if "label" not in obj:
            raise BackendError(f"Group {obj} is missing property 'label'.")

        if not isinstance(obj.get("label"), str):
            raise BackendError(
                f"Property 'label' in device {obj} has wrong type "
                f"{type(obj.get('label'))}, expcted: str."
            )

        if "children" not in obj:
            raise BackendError(f"Group {obj} is missing property 'children'.")

        if not isinstance(obj.get("children"), list):
            raise BackendError(
                f"Property 'children' in device {obj} has wrong type "
                f"{type(obj.get('children'))}, expcted: list."
            )

        if len(obj) != 2:
            raise BackendError(
                f"Group {obj} has wrong amount of properties, expected "
                f"['label','children']"
            )

        if len(obj.get("children")) == 0:
            self._logger.warn(f"Group {obj} is a group without children.")

        group = TreeItemGroup()
        group.label = obj.get("label")
        group.parents = [parent]
        self._add_unique_id(group, parent)

        group.children = self._object_list_to_tree_item_list(
            obj.get("children"), group
        )
        return group

    def _add_unique_id(self, tree_item: TreeItem, parent: TreeItemGroup):

        # Use (cryptographic) hash of the items label for the id in order to
        # keep the same id across runs.
        # This hides the deviceId of the smartplugs from the clients and gives
        # ids to groups as well.
        hash_source: str = tree_item.label

        if parent is not None:
            # index 0 because parent has to be a group, those have only ever
            # one id
            hash_source += parent.ids[0]

        tree_item_id: str = hashlib.sha256(str.encode(hash_source)).hexdigest()
        while tree_item_id in self._id_to_tree_item_mapping:
            # if the label is not unique in the file change the hash source
            # (deterministically) until a unique hash is created
            hash_source += "0"
            tree_item_id = hashlib.sha256(str.encode(hash_source)).hexdigest()

        tree_item.ids.append(tree_item_id)
        self._id_to_tree_item_mapping[tree_item_id] = tree_item

    def _collect_dependencies(self, device_objs: list):
        """

        TODO: warning: does not use mutex

        """

        graph_edges: list[tuple[str]] = []

        def convert_ids_to_references(obj: dict):

            if "turn_off_if_all_in_list_are_off" not in obj:
                return

            tree_item: TreeItemDevice = self._deviceId_to_device_mapping.get(
                obj.get("deviceId")
            )

            for deviceId in obj["turn_off_if_all_in_list_are_off"]:

                if deviceId not in self._deviceId_to_device_mapping:

                    raise BackendError(
                        f"Specified deviceId {deviceId} in "
                        f"'turn_off_if_all_in_list_are_off' of device "
                        f"{obj} does not exist."
                    )
                trigger_item: TreeItemDevice = (
                    self._deviceId_to_device_mapping[deviceId]
                )
                tree_item.turn_off_if_all_in_list_are_off.append(trigger_item)
                trigger_item.other_devices_listening_for_this_device_switching_off.append(
                    tree_item
                )
                graph_edges.append((trigger_item.deviceId, tree_item.deviceId))

        for obj in device_objs:
            convert_ids_to_references(obj)

        graph = networkx.DiGraph(graph_edges)
        cycles = networkx.recursive_simple_cycles(graph)

        if len(cycles) != 0:
            raise BackendError(
                f"The dependencies formed by 'turn_off_if_all_in_list_are_off' "
                f"result in cyclic dependencies: {cycles}"
            )

    def get_device_tree_dicts(self) -> list[dict]:
        """Function to answer a call to /gettree, returns the current state of
        the tree.

        @return A hierarchy of dictionaries and lists representing the current
        state of the device tree.
        """

        return self._tree.to_dict(None)

    def get_item(self, id: str) -> TreeItem:

        return self._id_to_tree_item_mapping.get(id)

    def get_device(self, deviceId: str) -> TreeItemDevice:

        return self._deviceId_to_device_mapping.get(deviceId)
