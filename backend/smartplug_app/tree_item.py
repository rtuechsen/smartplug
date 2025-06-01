"""Contains classes for storing and manipulating the hierarchy of devices and
groups.
"""

import datetime
from .admin_settings import SWITCHING_TOGGLE_DELAY


class TreeItem:
    """A data class that groups common properties of a tree items."""

    def __init__(self):
        """Constructor for the class."""

        ## The human readable label of the item. Used when displaying the item
        ## in a UI.
        self.label: str = None

        # TODO: Explain: ids[0] belongs to parents[0]
        ## The unique id of the item. A string of hexadecimal digits of length
        ## 64. Ignores the similarity to pythons build-in 'id' to match the
        ## name of the variable across the project. The first id in this list
        ## corresponds to the first group in self.parents and so on.
        self.ids: list[str] = []

        ## A boolean indicating if the item should be turned ON (True) or OFF
        ## (False). Ignores PEP8 naming convention to match the name of the
        ## variable across the project.
        self._isOn: bool = False

        ## A boolean indicating if the item is currently reachable. Ignores
        ## PEP8 naming convention to match the name of the variable across the
        ## project.
        self._isAvailable: bool = False

        ## The list of groups that have this item as a child. The first group
        ## in this list corresponds to the first id in self.ids and so on.
        self.parents: list[TreeItemGroup | None] = []

    def get_isOn(self) -> bool:
        """Function to get the current state of _isOn.

        @return A boolean indicating if the item should be turned ON (True) or
        OFF (False).
        """
        return self._isOn

    def set_isOn(self, new_isOn: bool) -> None:
        """Function to set the value of _isOn.

        Changes are automatically propagated up to the parents.

        @param new_isOn The value that _isOn should adopt.
        """

        if new_isOn != self._isOn:
            self._isOn = new_isOn

            # Only propagate changes if there was an actual change.
            for parent in self.parents:
                if parent is None:
                    # This is the case for the the group at the root of the
                    # tree.
                    continue
                parent.update_isOn_from_children()

    def get_isAvailable(self) -> bool:
        """Function to get the current state of _isAvailable.

        @return A boolean indicating if the item is currently reachable.
        """

        return self._isAvailable

    def set_isAvailable(self, new_isAvailable: bool) -> None:
        """Function to set the value of _isAvailable.

        Changes are automatically propagated up to the parents.

        @param new_isAvailable The value that _isAvailable should adopt.
        """

        if new_isAvailable != self._isAvailable:
            self._isAvailable = new_isAvailable

            # Only propagate changes if there was an actual change.
            for parent in self.parents:
                if parent is None:
                    # This is the case for the the group at the root of the
                    # tree.
                    continue
                parent.update_isAvailable_from_children()


class TreeItemDevice(TreeItem):
    """A data class that holds common properties of a device."""

    def __init__(self):
        """Constructor for the class.

        This function also initializes time_last_switched to a reasonable
        value.
        """

        super().__init__()

        ## The unique id that is set on the smartplug. Ignores PEP8 naming
        ## convention to match the name of the variable across the project.
        self.deviceId: str = None

        ## The time this device was last switched. Used to conform to the per
        ## device switching delay.
        ## It is initialized to a value of (now - SWITCHING_TOGGLE_DELAY) in
        ## order to allow switching right after starting the server.
        self.time_last_switched: (
            datetime.datetime
        ) = datetime.datetime.now() - datetime.timedelta(
            seconds=SWITCHING_TOGGLE_DELAY
        )

        ## A List of devices. If all devices in that list are turned OFF, so
        ## should this device.
        self.turn_off_if_all_in_list_are_off: list[TreeItemDevice] = []

        ## A list of devices that are watching this device's _isOn state. Used
        ## to inform those devices in case this items state changes.
        self.other_devices_listening_for_this_device_switching_off: list[
            TreeItemDevice
        ] = []

    def to_dict(self, parent: "TreeItemGroup" | None) -> dict:
        """Function to convert the class to a dictionary.

        @param parent The group that is holding the list. None in case of the
        root group of the tree.

        @return A dictionary representing the current state of the device.
        """

        if parent is None:
            id = self.ids[0]
        else:
            # Because the first id in self.ids corresponds to the first group in
            # parents we can use index here.
            id = self.ids[self.parents.index(parent)]
        return {
            "label": self.label,
            "id": id,
            "isOn": self._isOn,
            "isAvailable": self._isAvailable,
        }


class TreeItemGroup(TreeItem):
    """A data class that holds common properties of a group."""

    def __init__(self):
        """Constructor for the class."""
        super().__init__()

        ## A list of TreeItems that this group holds.
        self.children: "list[TreeItemDevice|TreeItemGroup]" = []

    def to_dict(self, parent: "TreeItemGroup") -> dict:
        """Converts the class to a hierarchy of dictionaries and lists.

        @param parent The group that is holding the list. None in case of the
        root group of the tree.

        @return A dictionary representing the current state of the group.
        """

        # The parent argument is not used here but is kept to match the
        # signature of TreeItemDevice.to_dict().

        # We collect the data from all direct children, using a recursive call.
        children_dict: list[dict] = [
            child.to_dict(self) for child in self.children
        ]

        # We use index 0 here because the parent is a group and those have
        # only ever a single id.
        return {
            "label": self.label,
            "id": self.ids[0],
            "isOn": self._isOn,
            "isAvailable": self._isAvailable,
            "children": children_dict,
        }

    def _compute_isOn_from_children(self) -> bool:
        """Function to re-evaluate the state of _isOn based on this groups
        children.

        @return A boolean indicating if the item should be turned ON (True) or
        OFF (False).
        """

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
        """Function to re-evaluate the state of _isAvailable based on this
        groups children.

        @return A boolean indicating if the item is currently reachable.
        """

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
        """Function to re-evaluate the state of _isOn based on this groups
        children.
        """

        new_isOn = self._compute_isOn_from_children()
        self.set_isOn(new_isOn)

    def update_isAvailable_from_children(self) -> None:
        """Function to re-evaluate the state of _isAvailable based on this
        groups children.
        """

        new_isAvailable = self._compute_isAvailable_from_children()
        self.set_isAvailable(new_isAvailable)
