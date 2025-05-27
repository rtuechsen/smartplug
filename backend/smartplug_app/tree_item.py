"""Contains classes for storing the device tree."""

import datetime


# TODO: make ALL members protected, add getter and setter


class TreeItem:
    """A pure data class that groups common properties of a tree items."""

    def __init__(self):
        """Constructor for the class."""

        ## The human readable label of the item. Used when displaying the item
        ## in a UI.
        self.label: str

        ## The unique id of the item. A string of hexadecimal digits of length
        ## 64.
        self.id: str

        ## A boolean indicating if the item should be turned on (True) or off
        ## (False). Ignores PEP8 naming convention to match the name of the
        ## variable across the project.
        self._isOn: bool = False

        ## A boolean indicating if the item is currently reachable. Ignores
        ## PEP8 naming convention to match the name of the variable across the
        ## project.
        self._isAvailable: bool = False

        self.parents: list[TreeItemGroup] = []

    def get_isOn(self) -> bool:
        return self._isOn

    def set_isOn(self, new_isOn: bool):

        if new_isOn != self._isOn:
            self._isOn = new_isOn

            for parent in self.parents:
                if parent is None:
                    continue
                parent.update_isOn_from_children()

    def get_isAvailable(self) -> bool:
        return self._isAvailable

    def set_isAvailable(self, new_isAvailable: bool) -> None:

        if new_isAvailable != self._isAvailable:
            self._isAvailable = new_isAvailable

            for parent in self.parents:
                if parent is None:
                    continue
                parent.update_isAvailable_from_children()


class TreeItemDevice(TreeItem):
    """A data class that groups common properties of a device."""

    def __init__(self):
        """Constructor for the class."""

        super().__init__()

        ## The unique id that is set on the smartplug. Ignores PEP8 naming
        ## convention to match the name of the variable across the project.
        self.deviceId: str

        self.time_last_switched: datetime.datetime = datetime.datetime.now()

        ## TODO: list of TreeItemDevices
        self.turn_off_if_all_in_list_are_off: list[TreeItemDevice] = []

        ## TODO: list of TreeItemDevices
        self.other_devices_listening_for_this_device_switching_off: list[
            TreeItemDevice
        ] = []

    def to_dict(self) -> dict:
        """Converts the class to a dictionary.

        @return A dictionary representing the current state of the class.
        """
        return {
            "label": self.label,
            "id": self.id,
            "isOn": self._isOn,
            "isAvailable": self._isAvailable,
        }


class TreeItemGroup(TreeItem):
    """A data class that groups common properties of a group."""

    def __init__(self):
        """Constructor for the class."""
        super().__init__()

        ## A list of TreeItems that this group combines.
        self.children: "list[TreeItemDevice|TreeItemGroup]" = []

    def to_dict(self) -> dict:
        """Converts the class to a hierarchy of dictionaries and lists.

        @return A dictionary representing the current state of the class.
        """

        # collect the data from all direct children,
        # recursive call, will travel down the hierarchy
        children_dict: list[dict] = [
            child.to_dict() for child in self.children
        ]

        return {
            "label": self.label,
            "id": self.id,
            "isOn": self._isOn,
            "isAvailable": self._isAvailable,
            "children": children_dict,
        }

    def _compute_isOn_from_children(self) -> bool:

        children_isOn: list[bool] = [
            child.get_isOn() for child in self.children
        ]

        if all(children_isOn):
            return True

        children_isOn_negated: list[bool] = [
            None if state is None else not state for state in children_isOn
        ]

        if all(children_isOn_negated):
            return False

        return None

    def _compute_isAvailable_from_children(self) -> bool:

        children_isAvailable: list[bool] = [
            child.get_isAvailable() for child in self.children
        ]

        if all(children_isAvailable):
            return True

        children_isAvailable_negated: list[bool] = [
            None if state is None else not state
            for state in children_isAvailable
        ]

        if all(children_isAvailable_negated):
            return False

        return None

    def update_isOn_from_children(self) -> None:

        new_isOn = self._compute_isOn_from_children()
        self.set_isOn(new_isOn)

    def update_isAvailable_from_children(self) -> None:

        new_isAvailable = self._compute_isAvailable_from_children()
        self.set_isAvailable(new_isAvailable)
