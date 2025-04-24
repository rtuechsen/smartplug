
/******************************************************************************************
 * @packageDocumentation  ErrorDisplay.tsx
 * 
 * # TODO
 ******************************************************************************************/

import * as React from 'react';
import Button from '@mui/material/Button';
import Snackbar, { SnackbarCloseReason } from '@mui/material/Snackbar';
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';
import { JSX } from '@emotion/react/jsx-runtime';


interface ErrorDisplayProps {
	message: string;
	isOpenState: boolean;
}

// https://mui.com/material-ui/react-snackbar/#introduction

function ErrorDisplay({ message, isOpenState }: ErrorDisplayProps): JSX.Element {

	const handleClose = (
		event: React.SyntheticEvent | Event,
		reason?: SnackbarCloseReason,
	): void => {
		if (reason === 'clickaway') {
			return;
		}
		setOpen(false);
	};

	const action = (
		<React.Fragment>
			<Button color="secondary" size="small" onClick={handleClose}>
				UNDO
			</Button>
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
		<div>
			<Button onClick={handleClick}>Open Snackbar</Button>
			<Snackbar
				open={open}
				autoHideDuration={6000}
				onClose={handleClose}
				message="Note archived"
				action={action}
			/>
		</div>
	);
}

export default ErrorDisplay;