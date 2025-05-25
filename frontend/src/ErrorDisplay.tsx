
import * as React from 'react';
import Snackbar, { SnackbarCloseReason } from '@mui/material/Snackbar';
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';
import Alert from '@mui/material/Alert';
import { JSX } from '@emotion/react/jsx-runtime';

/**
 * A data structure to hold the callback for the displaying error messages.
 * 
 * Wrapping this in a callback instead of passing only the callback allows to extend other interfaces. 
 * It also is more consistent how we pass properties in other places.
 */
export interface DisplayErrorCallbackProps {

	/**
	 * The callback to use from various components if they want to trigger an error message.
	 * 
	 * @param message The error message to be displayed to the user.
	 * 
	 * @param returnToLoginPage Whether the app should return to the login page. This argument is optional, the default value is `false`.
	 * 
	 * @returns A void Promise that can be waited on if one wants to wait for the function to complete.
	 */
	displayError: (message: string, returnToLoginPage?: boolean) => Promise<void>;
}

/**
 * A Data structure to pass information to the error display.
 */
export interface ErrorDisplayProps {

	/**
	 * The error message to display.
	 */
	message: string;

	/**
	 * If the error is open or hidden from the user.
	 */
	isErrorOpen: boolean;

	/**
	 * A setter for the 'isErrorOpen' state. Required because the state is owned by the App but the error display needs to be able to close itself.
	 */
	setIsErrorOpen: React.Dispatch<React.SetStateAction<boolean>>;
}

/**
 * A component that uses a Snackbar to display error messages to the user.
 * This is meant to be used throughout the frontend to report problems to the user.
 * 
 * reference: https://mui.com/material-ui/react-snackbar/#introduction
 * 
 * @param props Holds the data needed to construct the error display.
 * 
 * @returns The react component of the error display.
 */
function ErrorDisplay({ message, isErrorOpen, setIsErrorOpen }: ErrorDisplayProps): JSX.Element {

	const handleClose = (
		_: React.SyntheticEvent | Event,
		reason?: SnackbarCloseReason,
	): void => {
		if (reason === 'clickaway') {
			return;
		}
		setIsErrorOpen(false);
	};

	const action = (
		<React.Fragment>
			<IconButton
				size="small"
				aria-label="close"
				color="inherit"
				onClick={handleClose}
			>
				<CloseIcon fontSize="small" />
			</IconButton>
		</React.Fragment>
	);

	return (
		<Snackbar
			anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
			open={isErrorOpen}
			onClose={handleClose}
			action={action}
		>
			<Alert
				onClose={handleClose}
				severity="error"
				variant="filled"
			>
				{message}
			</Alert>
		</Snackbar>
	);
}

export default ErrorDisplay;