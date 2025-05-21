// TODO: improve imports everywhere similarly to here ??? (grouping)
import { Paper, Stack, TextField, Box, IconButton } from "@mui/material";
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import KeyRounded from '@mui/icons-material/KeyRounded';
import PersonRounded from '@mui/icons-material/PersonRounded';
import { JSX } from '@emotion/react/jsx-runtime';
import React from "react";
import { LoadingButton } from "./LoadingButtonGroup";


interface LoginProps {
	onLoginSuccess: () => void;
	displayError: (message: string) => Promise<void>;
}

function Login({ onLoginSuccess, displayError }: LoginProps): JSX.Element {
	const [showPassword, setShowPassword] = React.useState(false);
	const [password, setPassword] = React.useState('');
	const [username, setUsername] = React.useState('');

	// Create an empty ref for the sign-in-button.
	// This ref will be passed to the button, afterwards the button is accessible here using that ref.
	// This is used in order to click the button using the enter key.
	const signInButtonRef = React.useRef<HTMLButtonElement>(null);

	// Toggle the showing state for the password
	function handleClickShowPassword(): void {
		setShowPassword((show) => !show);
	}

	// Prevents the browser from deselecting the input field when clicking a button
	function preventFieldDeselect(event: React.MouseEvent<HTMLButtonElement>): void {
		event.preventDefault();
	};

	// Is executed when trying to sign in using the "Sign In"-button
	async function signIn(username: string, password: string): Promise<void> {
		const response: Response = await fetch('/api/login/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				username: username,
				password: password,
			}),
		});

		if (response.ok) {
			onLoginSuccess();
		} else {
			const responseData = await response.json();
			displayError(`${response.status} ${response.statusText}: ${responseData.message}`);
		}

	};

	// credit: https://stackoverflow.com/a/59147255
	// Click the sign-in-button using the enter key.
	React.useEffect(() => {
		// Add an event listener for (both) enter key(s).
		function listener(event): void {
			if (event.code === "Enter" || event.code === "NumpadEnter") {
				event.preventDefault();
				// Check if the ref is already populated and then click the button.
				if (signInButtonRef.current) {
					signInButtonRef.current.click();
				}
			}
		};
		document.addEventListener("keydown", listener);
		// Remove the listener afterwards.
		return function (): void {
			document.removeEventListener("keydown", listener);
		};
	}, [username, password]);

	return (
		<Paper
			elevation={2}
			sx={{
				display: 'grid',
				gridTemplateColumns: 'auto auto auto',
				gridTemplateRows: 'auto auto auto',
				gap: '1rem',
				padding: '1.5rem',
				alignItems: 'center',
				justifyItems: 'start',
				width: 'fit-content',
			}}
		>
			<PersonRounded sx={{ alignSelf: 'end', mb: '0.5rem' }} />
			<TextField
				id="input-username"
				label="Username"
				variant="standard"
				onChange={(e) => setUsername(e.target.value)}
				autoFocus
				sx={{ width: '20rem' }}
			/>
			<Box />

			<KeyRounded sx={{ alignSelf: 'end', mb: '0.5rem' }} />
			<TextField
				id="input-password"
				label="Password"
				variant="standard"
				type={showPassword ? 'text' : 'password'}
				onChange={(e) => setPassword(e.target.value)}
				sx={{ width: '20rem' }}
			/>
			<IconButton
				onClick={handleClickShowPassword}
				onMouseDown={preventFieldDeselect}
				onMouseUp={preventFieldDeselect}
				sx={{ alignSelf: 'end' }}
			>
				{showPassword ? <VisibilityOff /> : <Visibility />}
			</IconButton>

			<Box />
			<Box sx={{ justifySelf: 'end' }}>
				<LoadingButton
					variant='contained'
					onClick={() => signIn(username, password)}
					sx={{}}
					ref={signInButtonRef}
				>
					sign in
				</LoadingButton>
			</Box>
			<Box />
		</Paper>
	);
}

export default Login;