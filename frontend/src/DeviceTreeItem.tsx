
/******************************************************************************************
 * @packageDocumentation  DeviceTreeItem.tsx
 * 
 * # TODO
 ******************************************************************************************/

import * as React from 'react';
import { TreeItem2, TreeItem2Props } from '@mui/x-tree-view/TreeItem2';
import { useTreeItem2 } from '@mui/x-tree-view/useTreeItem2';
import { DeviceTreeItemLabel, DeviceTreeItemLabelProps } from './DeviceTreeItemLabel';
import DeviceTreeItemData from './DeviceTreeItemData';

/**
 * Tree item to be passed to RichTreeViews item slot
 *
 * This construct is needed according to the documentation (https://mui.com/x/react-tree-view/tree-item-customization/#usetreeitem2).
 * Allows us to set a custom label (DeviceTreeItemLabel).
 */
const DeviceTreeItem = React.forwardRef(function DeviceTreeItem(
	props: TreeItem2Props,
	ref: React.Ref<HTMLLIElement>,
) {
	/**
	 * Code needed according to the documentation to get the DeviceTreeItemData we passed to the tree.
	 */
	const { itemId } = props;
	const { publicAPI } = useTreeItem2({ itemId: itemId, rootRef: ref });
	const itemData = publicAPI.getItem(itemId) as DeviceTreeItemData;

	/**
	 * The two states of each tree item (isOn, isAvailable) are stored in states to trigger updates when those change
	 */
	const [isOnState, setIsOnState] = React.useState<boolean>(itemData.isOn);
	const [isAvailableState, setIsAvailableState] = React.useState<boolean>(itemData.isAvailable);

	/**
	 * When we pass new data to the tree this will trigger this function to set the item state isOn accordingly
	 */
	React.useEffect(() => {
		if (itemData.isOn !== isOnState) {
			setIsOnState(itemData.isOn);
		}
	}, [itemData.isOn]);	// watches for changes of isOn in tree data

	/**
	 * When we pass new data to the tree this will trigger this function to set the item state isAvailable accordingly
	 */
	React.useEffect(() => {
		if (itemData.isAvailable !== isAvailableState) {
			setIsAvailableState(itemData.isAvailable);
		}
	}, [itemData.isAvailable]);	// watches for changes of isAvailable in tree data

	return (
		/**
		 * Code needed according to the documentation to pass the custom label to the tree items slot
		 */
		<TreeItem2
			{...props}
			ref={ref}
			slots={{
				label: DeviceTreeItemLabel,
			}}
			slotProps={{
				label: {
					label: itemData.label,	// pass label as fixed data
					id: itemData.id,		// pass id as fixed data
					isOn: isOnState,		// pass isOn state as variable state
					isAvailable: isAvailableState,	// pass isAvailable state as variable state
					isGroup: itemData.children == undefined ? false : true		// let the label know if it is a device or group
				} as DeviceTreeItemLabelProps,
			}}
		/>
	);
});


export default DeviceTreeItem;