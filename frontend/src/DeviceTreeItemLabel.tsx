
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import { JSX } from '@emotion/react/jsx-runtime';
import LoadingButtonGroup from './LoadingButtonGroup';
import { AvilableIcon, OnIcon } from './StatusIcons';
import { DisplayErrorCallbackProps } from './ErrorDisplay';


/**
 * Data structure to pass information to each tree item
 */
export interface DeviceTreeItemLabelProps extends DisplayErrorCallbackProps {
	label: string;
	id: string;
	isOn: boolean;
	isAvailable: boolean;
	isGroup: boolean;
}


/**
 * A custom label for the tree view containing status icons and buttons
 *
 * Used for the label slot of the TreeItem2 component (DeviceTreeItem.tsx).
 * 
 * @param labelProperty of type DeviceTreeItemLabelProps that holds the data needed to construct the label.
 * 
 * @return the react component of the label
 */
export function DeviceTreeItemLabel({ label, id, isOn, isAvailable, isGroup, displayError }: DeviceTreeItemLabelProps): JSX.Element {

	return (
		<Stack
			direction='row'
			justifyContent='space-between'
			spacing={8}
			flexGrow={1}
		>
			<Typography sx={{ display: 'flex', alignItems: 'center', lineHeight: 1, whiteSpace: 'nowrap' }}>
				{label}
			</Typography>

			<Stack
				direction='row'
				justifyContent='right'
				spacing={4}
				flexGrow={1}
				alignItems='center'
			>
				<AvilableIcon isAvailable={isAvailable} isGroup={isGroup} />
				<OnIcon isOn={isOn} isGroup={isGroup} />
				<LoadingButtonGroup id={id} displayError={displayError} />
			</Stack>
		</Stack>
	);
}


