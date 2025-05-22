
import * as React from 'react';
import ButtonGroup from '@mui/material/ButtonGroup';
import Button from '@mui/material/Button';
import { JSX } from '@emotion/react/jsx-runtime';
import { getCsrfToken } from './RequestTools';
import { DisplayErrorCallbackProps } from './ErrorDisplay';
import type { OverridableStringUnion } from '@mui/types';
import type { ButtonPropsVariantOverrides } from '@mui/material/Button';


/**
 * A data structure to pass information to an LoadingButton.  
 */
export interface LoadingButtonProps {

	/**
	 * The (async) callback used when clicking the button. 
	 * 
	 * @returns A void Promise that can be waited on if one wants to wait for the function to complete.
	 */
	onClick: () => Promise<void>;
	variant?: OverridableStringUnion<'text' | 'outlined' | 'contained', ButtonPropsVariantOverrides>;
	sx?: object;
	ref?: React.Ref<HTMLButtonElement>;
}


/**
 * A button that shows a loading circle while waiting for its callback to finish.  
 * 
 * @param props The properties needed to construct the button.
 * 
 * @return The react component of the button.
 */
export function LoadingButton({ onClick, variant, children, sx, ref }: React.PropsWithChildren<LoadingButtonProps>): JSX.Element {

	// state that decides wheter to show a loading circle or not, triggers the button to update when state changes
	const [loading, setLoading] = React.useState<boolean>(false);

	/**
	 * Wrapper function to wrap the callback of the button between changes to the loading state.
	 * 
	 * @return A void Promise that can be waited on if one wants to wait for the function to complete.
	 */
	async function handleClick(): Promise<void> {
		setLoading(true);
		await onClick();
		setLoading(false);
	}

	// TODO: verify that new error messages replace older ones in the UI

	return (
		<Button
			onClick={handleClick}
			loading={loading}
			sx={{ whiteSpace: 'nowrap', ...sx }}
			variant={variant || 'text'}
			ref={ref}
		>
			{children}
		</Button>
	);
}


/**
 * A data structure to pass information to an LoadingButtonGroup.  
 */
export interface LoadingButtonGroupProps extends DisplayErrorCallbackProps {

	/**
	 * The id of the tree item this button groups belongs to. Used to make API calls to switch items on or off.
	 */
	id: string;
}


/**
 * A combined group of 'ON' and 'OFF' button which each show a loading circle while waiting for its callback to finish.
 *
 * @param props Holds the data needed to construct the button.
 * 
 * @return The react component of the button group.
 */
function LoadingButtonGroup({ id, displayError }: LoadingButtonGroupProps): JSX.Element {

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
			headers: {
				'X-CSRFToken': await getCsrfToken(),	// need the CSRF token for POST requests
				'Content-type': 'application/json; charset=UTF-8'
			},
			credentials: 'include',
			mode: 'same-origin',	// prevents sending token to another website
			body: JSON.stringify({
				id: id,
				desired_isOn: desired_isOn
			}),
		});

		if (!response.ok) {
			const responseData = await response.json();
			await displayError(`${response.status} ${response.statusText}: ${responseData.message}`);
		}
	}

	return (
		<ButtonGroup variant="outlined" size="small">
			<LoadingButton onClick={async () => { await sendSwitchRequest(true); }}>Turn on</LoadingButton>
			<LoadingButton onClick={async () => { await sendSwitchRequest(false); }}>Turn off</LoadingButton>
		</ButtonGroup>
	);
}


export default LoadingButtonGroup;