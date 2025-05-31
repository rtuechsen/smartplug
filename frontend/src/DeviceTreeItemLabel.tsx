
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import { JSX } from '@emotion/react/jsx-runtime';
import LoadingButtonGroup from './LoadingButtonGroup';
import { OnIcon, AvailableIcon } from './StatusIcons';
import { DisplayErrorCallbackProps } from './ErrorDisplay';
import { getCsrfToken } from './RequestTools';


/**
 * A data structure to pass information to each tree item.
 */
export interface DeviceTreeItemLabelProps extends DisplayErrorCallbackProps {

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
	 * If the item is a group or a device.
	 */
	isGroup: boolean;
}


/**
 * A custom label for the tree view containing status icons and buttons
 *
 * Used for the label slot of the TreeItem2 component (DeviceTreeItem.tsx).
 * 
 * @param props Holds the data needed to construct the label.
 * 
 * @return The react component of the label.
 */
export function DeviceTreeItemLabel({ label, id, isOn, isAvailable, isGroup, displayError }: DeviceTreeItemLabelProps): JSX.Element {

	/**
	 * Function to send the switch request to the API.
	 * 
	 * @param desired_isOn If the group or device should be turned on (true) or off (false).
	 * 
	 * @return A void promise indicating that the functions has returned.
	 */
	async function sendSwitchRequest(desired_isOn: boolean): Promise<void> {
		const response = await fetch('/api/switch/', {
			method: 'POST',
			credentials: 'include',
			mode: 'same-origin',	// prevents sending token to another website
			headers: {
				'X-CSRFToken': await getCsrfToken(),	// need the CSRF token for POST requests
				'Content-type': 'application/json; charset=UTF-8'
			},
			body: JSON.stringify({
				id: id,
				desired_isOn: desired_isOn
			}),
		});

		if (!response.ok) {
			const responseData = await response.json();
			await displayError(`${response.status} ${response.statusText}: ${responseData.detail}`);
		}
	}

	return (
		<Stack
			direction='row'
			justifyContent='space-between'
			spacing={'3rem'}
			flexGrow={1}
		>
			<Typography sx={{ display: 'flex', alignItems: 'center', lineHeight: 1, whiteSpace: 'nowrap' }}>
				{label}
			</Typography>

			<Stack
				direction='row'
				justifyContent='right'
				spacing={'1.5rem'}
				flexGrow={1}
				alignItems='center'
			>
				<AvailableIcon isAvailable={isAvailable} isGroup={isGroup} />
				<OnIcon isOn={isOn} isGroup={isGroup} />
				<LoadingButtonGroup onClickLeft={() => sendSwitchRequest(true)} onClickRight={() => sendSwitchRequest(false)} />
			</Stack>
		</Stack>
	);
}


