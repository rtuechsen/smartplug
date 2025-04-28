
import * as React from 'react';
import Snackbar, { SnackbarCloseReason } from '@mui/material/Snackbar';
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';
import Alert from '@mui/material/Alert';
import { JSX } from '@emotion/react/jsx-runtime';


export interface DisplayErrorCallbackProps {
	displayError: (message: string) => Promise<void>;
}


interface ErrorDisplayProps {
	message: string;
	isErrorOpen: boolean;
	setIsErrorOpen: React.Dispatch<React.SetStateAction<boolean>>;
}

// https://mui.com/material-ui/react-snackbar/#introduction

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