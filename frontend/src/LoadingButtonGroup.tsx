
/******************************************************************************************
 * @packageDocumentation  LoadingButtonGroup.tsx
 * 
 * # TODO
 ******************************************************************************************/

import * as React from 'react';
import ButtonGroup from '@mui/material/ButtonGroup';
import Button from '@mui/material/Button';
import { JSX } from '@emotion/react/jsx-runtime';
import { getCsrfToken } from './RequestTools';


/**
 * Data structure to pass information to an LoadingButton.  
 *
 * onClick holds the callback for the button and accepts an async function.  
 */
interface LoadingButtonProps {
	onClick: () => Promise<void>;
}


/**
 * A button that shows a loading circle while waiting for its callback to finish.  
 * 
 * @param buttonProperty of type LoadingButtonProps that holds the data needed to construct the button.
 * 
 * @return the react component of the button
 */
function LoadingButton({ onClick, children }: React.PropsWithChildren<LoadingButtonProps>): JSX.Element {

	/**
	 * state that decides wheter to show a loading circle or not, triggers the button to update when state changes
	 */
	const [loading, setLoading] = React.useState<boolean>(false);

	/**
	 * Wrapper function to wrap the callback of the button between changes to the loading state
	 * 
	 * @return a void promise indicating that the functions has returned
	 */
	async function handleClick(): Promise<void> {
		setLoading(true);
		await onClick();
		setLoading(false);
	}

	return (
		<Button
			onClick={handleClick}
			loading={loading}
			sx={{ whiteSpace: 'nowrap' }}
		>
			{children}
		</Button>
	);
}


/**
 * Data structure to pass information to an LoadingButtonGroup.  
 */
interface LoadingButtonGroupProps {
	id: string;
}


/**
 * A combined group of 'ON' and 'OFF' button which each show a loading circle while waiting for its callback to finish
 *
 * @param buttonGroupProperty of type LoadingButtonProps that holds the data needed to construct the button.
 * 
 * @return the react component of the button group
 */
function LoadingButtonGroup({ id }: LoadingButtonGroupProps): JSX.Element {

	/**
	 * Function to send the switch request to the API
	 * 
	 * @param isOn if the group or device should be turned on (true) or off (false)
	 * 
	 * @return a void promise indicating that the functions has returned
	 */
	async function sendSwitchRequest(isOn: boolean): Promise<void> {
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
				isOn: isOn
			}),
		});
		// TODO: handle error
		await response.json();
		console.log(response);
	}

	return (
		<ButtonGroup variant="outlined" size="small">
			<LoadingButton onClick={async () => { await sendSwitchRequest(true); }}>Turn on</LoadingButton>
			<LoadingButton onClick={async () => { await sendSwitchRequest(false); }}>Turn off</LoadingButton>
		</ButtonGroup>
	);
}


export default LoadingButtonGroup;