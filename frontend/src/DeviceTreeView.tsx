
/******************************************************************************************
 * @packageDocumentation  DevicesTreeView.tsx
 * 
 * # TODO
 ******************************************************************************************/

import * as React from 'react';
import Box from '@mui/material/Box';
import { RichTreeView } from '@mui/x-tree-view/RichTreeView';
import { TreeItem2Props } from '@mui/x-tree-view/TreeItem2';
import { SlotComponentPropsFromProps } from '@mui/x-tree-view/internals/models';
import { TreeViewItemId } from '@mui/x-tree-view/models';
import { JSX } from '@emotion/react/jsx-runtime';
import DeviceTreeItemData from './DeviceTreeItemData';
import DeviceTreeItem from './DeviceTreeItem';
import { DisplayErrorCallbackProps } from './ErrorDisplay';

interface RichTreeViewItemSlotOwnerState {
	itemId: TreeViewItemId;
	label: string;
}

/**
 * The Tree View that displays all devices and groups in a hierarchy
 *
 * Allows to view and controll devices and groups.
 * 
 * @return the react component of the tree view
 */
function DeviceTreeView({ displayError }: DisplayErrorCallbackProps): JSX.Element {

	const ref = React.useRef<HTMLDivElement>(null);

	/**
	 * state for holding the data of the tree, triggers updates to the tree if the data changes
	 */
	const [deviceTreeDataState, setDeviceTreeDataState] = React.useState<DeviceTreeItemData[]>();

	/**
	 * The problem: 
	 * We need to adjust the trees width to hold all labels, but not (much) wider. But because
	 * collapsed tree items are not taken into account this would lead to the tree changing its width on 
	 * collapsing/expanding items.
	 * The solution:
	 * We fully expand the tree, measure its width and set this as the fixed width (note that this will not
	 * take changes to the tree labels into account and requires a page reload to display the changes properly
	 * if the admin changes the configuration while the site is displayed).
	 * useLayoutEffect() (in contrast to useEffect() ) runs at a point in time where the components and their 
	 * dimensions are already knwon. This is needed to measure the width of the tree. But because the data for
	 * the tree needs to be fetched from the backend this function has already run by the time the data is available.
	 * To trigger that function again after the data arrived we use the following state bool as a dependency 
	 * for useLayoutEffect(). Changes to that state bool will trigger the function again.  
	 */
	const [deviceTreeDataArrivedState, setDeviceTreeDataArrivedState] = React.useState<boolean>(false);

	/**
	 * To expand all tree items one has to collect all ids and pass them to the RichTreeView. This is 
	 * stored in a state to trigger the tree to update once the data is available.  
	 */
	const [expandedIdsState, setExpandedIdsState] = React.useState<string[]>([]);

	/**
	 * useEffect() is more performant than useLayoutEffect(), it is used to fetch the tree data from the api,
	 * collect the all ids (used for expanding) and then trigger useLayoutEffect() to measure the width
	 * of the tree.  
	 */
	React.useEffect(() => {

		/**
		 * declare an async function to fetch and process the data
		 */
		async function getTree(): Promise<void> {

			/**
			 * fetch the tree data
			 */
			const response = await fetch('/api/gettree/', {
				method: 'GET',
				credentials: 'include',
				mode: 'same-origin',	// prevents sending token to another website
			});

			const responseData = await response.json();

			if (!response.ok) {
				displayError(`${response.status} ${response.statusText}: ${responseData.message}`);
				// abort tree view creation
				return;
			}

			const treeData = responseData as DeviceTreeItemData[]; // convert JSON to hierarchy of interfaces

			/**
			 * set the state with it to trigger the tree to update
			 */
			setDeviceTreeDataState(treeData);

			const treeItemIds: string[] = [];
			/**
			 * recursively collects all ids found in the data passed and adds them
			 * to an array
			 * @param data an tree item of type DeviceTreeItemData
			 */
			function collectIds({ id, children }: DeviceTreeItemData): void {
				treeItemIds.push(id);
				if (children) {
					children.forEach((child) => { collectIds(child); });
				}
			}

			/**
			 * collect all ids and set the state to trigger the tree to update
			 */
			treeData.forEach((treeItem) => { collectIds(treeItem); });
			setExpandedIdsState(treeItemIds);

			/**
			 * set the state bool to trigger useLayoutEffect()
			 */
			setDeviceTreeDataArrivedState(true);
		}

		/**
		 * start the async function, don't wait for it to finish
		 */
		getTree();

		/**
		 * create the event source for SSE
		 */
		const eventSource = new EventSource('/api/events/', {
			withCredentials: true
		});
		// TODO: can this fail? error handling!

		/**
		 * register a function to run when a SSE message arrives, converts the update to the tree view
		 * from JSON to interface and updates the state to trigger the tree to update
		 * @param event the SSE event, contains the message
		 */
		eventSource.onmessage = function (event): void {
			// TODO: can this fail? error handling!
			const treeData = JSON.parse(event.data) as DeviceTreeItemData[];
			setDeviceTreeDataState(treeData);
		};

		eventSource.onerror = function (): void {
			displayError('Server Sent Events (SSE) have failed.');
		};

		return function (): void {
			/**
			 * need to close EventSource to avoid subscribing twice in StrictMode (in StrictMode components will
			 * be mounted multiple times to detect side effects, see main.tsx)
			 */
			eventSource.close();
		};

	}, []);	// empty dependencies => will only run once after component mounted

	/**
	 * will run once the dimensions of the components are known, used to read the current width of the tree and set the
	 * width to that fixed size to avoid changing width on collapsing/expanding
	 */
	React.useLayoutEffect(() => {
		/**
		 * only run if the reference to the DOM element is valid and the state bool is set (the data has arrived and the tree is expanded)
		 */
		if (ref.current !== null && deviceTreeDataArrivedState) {
			/**
			 * using scrollWidth gives the width even if the component extends past the window
			 */
			ref.current.style.width = `${ref.current.scrollWidth}px`;
		}
	}, [deviceTreeDataArrivedState]);	// state bool given as dependency, will trigger useLayoutEffect() when state bool changes

	return (
		/**
		 * Box is configured to allow the tree to expand exactly as much as needed, not more.
		 * This is only needed at the beginning to measure the tree width.
		 */
		<Box ref={ref} sx={{ minHeight: 'max-content', width: 'fit-content' }}>
			{/**
			  * only display the tree once its data is ready and it is expanded
			  */}
			{deviceTreeDataState == undefined || expandedIdsState.length === 0 ?
				null :
				<RichTreeView
					items={deviceTreeDataState}		// the data for the tree, updates when the state changes
					slots={{ item: DeviceTreeItem as React.JSXElementConstructor<TreeItem2Props> }}	// a custom tree item that includes label, icons and buttons
					expansionTrigger='iconContainer'	// only collapse/expand when clicking the arrow, not the whole panel (interferes with buttons)
					slotProps={{ item: { displayError: displayError } as SlotComponentPropsFromProps<TreeItem2Props, object, RichTreeViewItemSlotOwnerState> }}
					itemChildrenIndentation={'1.5rem'}
					expandedItems={expandedIdsState}	// the ids of the items to expand, updates when the state changes
					onExpandedItemsChange={(_event, ids) => setExpandedIdsState(ids)}	// because we set the expanded items explicitly, user interaction will not work anymore => need to apply user interactions manually
				/>
			}
		</Box >
	);

}


export default DeviceTreeView;
