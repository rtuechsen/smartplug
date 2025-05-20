import { Paper, Stack, TextField, Box, IconButton, Button } from "@mui/material";
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import KeyRounded from '@mui/icons-material/KeyRounded';
import PersonRounded from '@mui/icons-material/PersonRounded';
import React from "react";
import { JSX } from '@emotion/react/jsx-runtime';


interface LoginProps {
	onLoginSuccess: () => void;
	displayError: (message: string) => Promise<void>;
}

function Login({ onLoginSuccess, displayError }: LoginProps): JSX.Element {
	const [showPassword, setShowPassword] = React.useState(false);
	const [password, setPassword] = React.useState('');
	const [username, setUsername] = React.useState('');

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


	return (
		<Paper
			elevation={10}
			sx={{
				width: '30rem',
				height: '30rem',
				alignItems: 'flex-start',
				justifyContent: 'center',
			}}>

			<Stack
				direction="column" spacing={2}
				sx={{
					justifyContent: 'space-evenly',
				}}>

				{/* TODO: Company Icon segment */}
				<Box>

				</Box>


				{/*Textual input segment*/}
				<Box>
					{/*Input-Field for username*/}
					<Box
						sx={{
							display: 'flex',
							alignItems: 'flex-end'
						}}>
						<PersonRounded sx={{ color: 'red', mr: '1rem', ml: '2rem' }} />
						<TextField
							id="input-username"
							label="Username"
							variant="standard"
							onChange={(e) => setUsername(e.target.value)} />
					</Box>

					{/*Input-Field for password*/}
					<Box
						sx={{
							display: 'flex',
							alignItems: 'flex-end'
						}}>
						<KeyRounded sx={{ color: 'red', mr: '1rem', ml: '2rem' }} />
						<TextField
							id="input-password"
							label="Password"
							variant="standard"
							type={showPassword ? 'text' : 'password'}
							onChange={(e) => setPassword(e.target.value)}
						/>
						<IconButton
							onClick={handleClickShowPassword}
							onMouseDown={preventFieldDeselect}
							onMouseUp={preventFieldDeselect}
						>
							{showPassword ? <VisibilityOff /> : <Visibility />}
						</IconButton>
					</Box>
				</Box>

				{/*Login Button segment*/}
				<Box
					sx={{
						display: 'flex',
						justifyContent: 'flex-end',
					}}>
					<Button
						variant='contained'
						onClick={() => signIn(username, password)}
						sx={{
							mr: '2rem',
							backgroundColor: 'red',
						}}
					>Sign In</Button>
				</Box>


			</Stack>
		</Paper>
	);
}

export default Login;