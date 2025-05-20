
import * as React from 'react';
import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { JSX } from '@emotion/react/jsx-runtime';
import DeviceTreeView from './DeviceTreeView';
import ErrorDisplay from './ErrorDisplay';
import Login from './Login';
import { getCsrfToken } from './RequestTools';


/**
 * The main App component.
 *
 * The function component for this website that includes all other components.  
 * It Contains the header area and the device tree.  
 * Also contains the color mode / theme.  
 * 
 * @return The react component of the main app.
 */
function App(): JSX.Element {
	const [isLoggedIn, setIsLoggedIn] = React.useState(false);
	const [currentErrorMessage, setCurrentErrorMessage] = React.useState<string>('');
	const [isErrorOpen, setIsErrorOpen] = React.useState<boolean>(false);

	function onLoginSuccess(): void {
		setIsLoggedIn(true);
	}

	async function displayError(message: string): Promise<void> {
		if (isErrorOpen) {
			// close previous error if still open
			// TODO: check if this works properly
			setIsErrorOpen(false);
		}
		setCurrentErrorMessage(message);
		setIsErrorOpen(true);
	}

	async function logout(): Promise<void> {

		const response = await fetch('/api/logout/', {
			method: 'POST',
			headers: {
				'X-CSRFToken': await getCsrfToken(),	// need the CSRF token for POST requests
				'Content-type': 'application/json; charset=UTF-8'
			},
			credentials: 'include',
			mode: 'same-origin',	// prevents sending token to another website
		});

		if (!response.ok) {
			const responseData = await response.json();
			displayError(`${response.status} ${response.statusText}: ${responseData.message}`);
		}
		else {
			setIsLoggedIn(false);
		}
	}

	const theme = createTheme({
		// even though only the dark theme is mentioned here, this will use the system preference of the user
		colorSchemes: {
			dark: true,
		},
	});

	return (
		// The ThemeProvider has to encapsulate the whole app.
		// Then a paper area is added to the top of the page to hold the title.
		// Below that a Box contains all items of the pages body, e.g. the DeviceTreeView.
		<ThemeProvider theme={theme}>
			<CssBaseline />	 {/* used to remove default padding of html body */}
			<Paper sx={{ padding: '2rem' }}>
				<Typography variant='h2' sx={{ whiteSpace: 'nowrap' }}>
					Smartplug Dirigent
				</Typography>
			</Paper>
			<Box sx={{ padding: '1.5rem' }}>
				{isLoggedIn ?
					<Stack
						direction='row'
						justifyContent='space-between'
						spacing={'1rem'}
					>
						<DeviceTreeView displayError={displayError} />
						<Button onClick={logout} variant='contained' sx={{ whiteSpace: 'nowrap', alignSelf: 'start', mr: '2rem', minWidth: 'fit-content' }}>Sign out</Button>
					</Stack>
					:
					<Login onLoginSuccess={onLoginSuccess} displayError={displayError} />
				}
				{/* ErrorDisplay is placed here but will only be shown if isErrorOpen is set */}
				<ErrorDisplay message={currentErrorMessage} isErrorOpen={isErrorOpen} setIsErrorOpen={setIsErrorOpen} />
			</Box>
		</ThemeProvider >
	);
}


export default App;
