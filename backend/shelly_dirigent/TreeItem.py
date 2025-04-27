from functools import reduce


class TreeItem:
    """Common parent class of devices and groups."""

    label: str
    id: str
    # TODO: add more specific type aliases for e.g. id ??? https://stackoverflow.com/questions/33045222/how-do-you-alias-a-type-in-python


class TreeItemDevice(TreeItem):
    deviceId: str
    isOn: bool
    isAvailable: bool
    # some variables in the device tree do not match the PEP8 naming convention, but it was important to us to match the naming of this
    # data across the project, i.e. the same variables will be spelled the same for backend, REST API and frontend

    def to_dict(self) -> dict:
        """Convert the class to a dictionary."""
        return {
            "label": self.label,
            "id": self.id,
            "isOn": self.isOn,
            "isAvailable": self.isAvailable,
        }


class TreeItemGroup(TreeItem):
    children: "list[TreeItemDevice|TreeItemGroup]"
    # note: does not hold isOn or isAvailable, those will be evaluated from its children before send out to the API

    def to_dict(self) -> dict:
        """Convert the class to a hierarchy of dictionaries and lists."""
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

        def combine_bools(a: bool, b: bool) -> bool | None:
            if a is True and b is True:
                return True
            elif a is False and b is False:
                return False
            else:
                return None

        if len(children_isOn) != 0:
            # no initial value passed because needed behavior cannot be achieved using reduce
            isOn: bool = reduce(combine_bools, children_isOn)
        else:
            isOn: bool = None

        if len(children_isAvailable) != 0:
            isAvailable: bool = reduce(combine_bools, children_isAvailable)
        else:
            isAvailable: bool = None

        return {
            "label": self.label,
            "id": self.id,
            "isOn": isOn,
            "isAvailable": isAvailable,
            "children": children_dict,
        }
