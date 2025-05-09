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

        self.turn_off_if_all_in_list_are_off: list[str]


class TreeItemDevice(TreeItem):
    """A data class that groups common properties of a device."""

    def __init__(self):
        """Constructor for the class."""

        super().__init__()

        ## The unique id that is set on the smartplug. Ignores PEP8 naming
        ## convention to match the name of the variable across the project.
        self.deviceId: str

        ## A boolean indicating if the item should be turned on (True) or off
        ## (False). Ignores PEP8 naming convention to match the name of the
        ## variable across the project.
        self.isOn: bool

        ## A boolean indicating if the item is currently reachable. Ignores
        ## PEP8 naming convention to match the name of the variable across the
        ## project.
        self.isAvailable: bool

        self.time_last_switched: datetime.datetime = datetime.datetime.now()

    def to_dict(self) -> dict:
        """Converts the class to a dictionary.

        @return A dictionary representing the current state of the class.
        """
        return {
            "label": self.label,
            "id": self.id,
            "isOn": self.isOn,
            "isAvailable": self.isAvailable,
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
        children_dict: list[dict] = []
        children_isOn: list[bool] = []
        children_isAvailable: list[bool] = []

        # collect the data from all direct children
        for child in self.children:
            child_dict = (
                child.to_dict()
            )  # recursive call, will travel down the hierarchy
            children_dict.append(child_dict)
            children_isOn.append(child_dict["isOn"])
            children_isAvailable.append(child_dict["isAvailable"])

        # decide state of group based on children

        isOn: bool = None
        isAvailable: bool = None

        # if all children states are True, so is the group

        if all(children_isOn):
            isOn = True

        if all(children_isAvailable):
            isAvailable = True

        children_isOn_negated: list[bool] = [
            not item for item in children_isOn
        ]

        children_isAvailable_negated: list[bool] = [
            not item for item in children_isAvailable
        ]

        # if all children states are False (i.e. all children states negated
        # are True), so is the group

        if all(children_isOn_negated):
            isOn = False

        if all(children_isAvailable_negated):
            isAvailable = False

        return {
            "label": self.label,
            "id": self.id,
            "isOn": isOn,
            "isAvailable": isAvailable,
            "children": children_dict,
        }
