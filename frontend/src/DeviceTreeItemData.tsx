
/******************************************************************************************
 * @packageDocumentation  DeviceTreeItemData.tsx
 * 
 * # TODO
 ******************************************************************************************/

/**
 * The definition of the main (hierarchical) data structure for holding the tree data in the frontend
 *
 * The property 'children' is optional. If present the item will be considered a group.
 */
interface DeviceTreeItemData {
	label: string;
	id: string;
	isOn: boolean;
	isAvailable: boolean;
	children?: DeviceTreeItemData[];
}


export default DeviceTreeItemData;