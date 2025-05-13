"""Contains classes for storing the device tree."""

import datetime


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

        self.parent: TreeItemGroup

    def get_isOn(self) -> bool:
        return self._isOn

    def set_isOn(self, new_isOn: bool):

        if new_isOn != self._isOn:
            self._isOn = new_isOn

            if self.parent is not None:
                self.parent.update_isOn_child(self._isOn)

    def get_isAvailable(self) -> bool:
        return self._isAvailable

    def set_isAvailable(self, new_isAvailable: bool) -> None:

        if new_isAvailable != self._isAvailable:

            self._isAvailable = new_isAvailable

            if self.parent is not None:
                self.parent.update_isAvailable_child(self._isAvailable)


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
        self.children: "list[TreeItemDevice|TreeItemGroup]"

    # note: does not hold isOn or isAvailable, those will be evaluated from its
    # children before send out to the API

    def to_dict(self) -> dict:
        """Converts the class to a hierarchy of dictionaries and lists.

        @return A dictionary representing the current state of the class.
        """

        # collect the data from all direct children
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

    def _compute_state_from_child_update(
        self, state_name: str, new_child_state: bool
    ) -> bool:

        self_state: bool = getattr(self, state_name)

        if len(self.children) == 1:
            return new_child_state

        if new_child_state is None:
            return None

        # need to compare children with each other

        if self_state is None:
            # need to compare with all children
            all_children_have_same_state: bool = all(
                [
                    new_child_state == getattr(some_child, state_name)
                    for some_child in self.children
                ]
            )
            if all_children_have_same_state:
                return new_child_state

        # all children had the same state before

        if self_state != new_child_state:
            return None

        # unusual, nothing changed
        return self_state

    def update_isOn_child(self, new_child_isOn: bool) -> None:

        new_isOn = self._compute_state_from_child_update(
            "_isOn", new_child_isOn
        )
        self.set_isOn(new_isOn)

    def update_isAvailable_child(self, new_child_isAvailable: bool) -> None:

        new_isAvailable = self._compute_state_from_child_update(
            "_isAvailable", new_child_isAvailable
        )
        self.set_isAvailable(new_isAvailable)
