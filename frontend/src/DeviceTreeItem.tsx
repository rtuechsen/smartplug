
import * as React from 'react';
import { TreeItem2, TreeItem2Props } from '@mui/x-tree-view/TreeItem2';
import { useTreeItem2 } from '@mui/x-tree-view/useTreeItem2';
import { JSX } from '@emotion/react/jsx-runtime';
import { DeviceTreeItemLabel, DeviceTreeItemLabelProps } from './DeviceTreeItemLabel';
import DeviceTreeItemData from './DeviceTreeItemData';
import { DisplayErrorCallbackProps } from './ErrorDisplay';

/**
 * A data structure that combines the TreeItem2Props required by the RichTreeView item slot with out own properties for triggering error messages.
 */
export interface DeviceTreeItemProps extends TreeItem2Props, DisplayErrorCallbackProps {

	afterButtonClick: () => Promise<void>;
}

/**
 * Tree item to be passed to RichTreeViews item slot
 *
 * This construct is needed according to the documentation (https://mui.com/x/react-tree-view/tree-item-customization/#usetreeitem2).
 * Allows us to set a custom label (DeviceTreeItemLabel).
 * 
 * @param props The properties needed to construct the item.
 * 
 * @param ref Allows getting a ref to the component instance. Required by the item slot of the RichTreeView.
 * 
 * @return The react component of the tree item.
 */
function DeviceTreeItem(props: DeviceTreeItemProps, ref: React.Ref<HTMLLIElement>): JSX.Element {

	// Code needed according to the documentation to get the DeviceTreeItemData we passed to the tree.
	const { itemId } = props;
	const { publicAPI } = useTreeItem2({ itemId: itemId, rootRef: ref });
	const itemData = publicAPI.getItem(itemId) as DeviceTreeItemData;

	// The two states of each tree item (isOn, isAvailable) are stored in states to trigger updates when those change.
	const [isOnState, setIsOnState] = React.useState<boolean>(itemData.isOn);
	const [isAvailableState, setIsAvailableState] = React.useState<boolean>(itemData.isAvailable);

	// When we pass new data to the tree this will trigger this function to set the item state isOn accordingly.
	React.useEffect(() => {
		if (itemData.isOn !== isOnState) {
			setIsOnState(itemData.isOn);
		}
	}, [itemData.isOn]);	// watches for changes of isOn in tree data

	// When we pass new data to the tree this will trigger this function to set the item state isAvailable accordingly.
	React.useEffect(() => {
		if (itemData.isAvailable !== isAvailableState) {
			setIsAvailableState(itemData.isAvailable);
		}
	}, [itemData.isAvailable]);	// watches for changes of isAvailable in tree data

	// Because TreeItem2 expects only TreeItem2Props as props, we need to split off our own props. Then we can pass each one spearately to the label.
	const { displayError, afterButtonClick, ...treeItem2Props } = props;

	return (
		// Code needed according to the documentation to pass the custom label to the tree items slot
		<TreeItem2
			{...treeItem2Props}
			ref={ref}
			slots={{
				label: DeviceTreeItemLabel,		// here we use our own label for the label slot
			}}
			slotProps={{
				label: {
					label: itemData.label,	// pass label as fixed data
					id: itemData.id,		// pass id as fixed data
					isOn: isOnState,		// pass isOn state as variable state
					isAvailable: isAvailableState,	// pass isAvailable state as variable state
					isGroup: itemData.children == undefined ? false : true,		// let the label know if it is a device or group
					displayError: displayError,	// here we pass our callback to trigger error messages
					afterButtonClick: afterButtonClick
				} as DeviceTreeItemLabelProps,
			}}
		/>
	);
}


export default DeviceTreeItem;