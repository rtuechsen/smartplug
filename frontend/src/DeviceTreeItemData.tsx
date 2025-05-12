
// TODO: de-duplicate DeviceTreeItemData, DeviceTreeItemLabelProps, OnIconProps, AvailableIconProps ???

/**
 * The definition of the main (hierarchical) data structure for holding the tree data in the frontend.
 *
 * The property 'children' is optional. If present the item will be considered a group.
 */
interface DeviceTreeItemData {

	/**
	 * The human readable label of the item. Used when displaying the item in a UI.
	 */
	label: string;

	/**
	 * The unique id of the item. A string of hexadecimal digits of length 64.
	 */
	id: string;

	/**
	 * A boolean indicating if the item should be turned on (True) or off (False). 
	 */
	isOn: boolean;

	/**
	 * A boolean indicating if the item is currently reachable.
	 */
	isAvailable: boolean;

	/**
	 * A list of TreeItems that this group combines. If defined the item is considered a group, not a device. While it does not make a lot of sense, the array can be empty.
	 */
	children?: DeviceTreeItemData[];
}


export default DeviceTreeItemData;