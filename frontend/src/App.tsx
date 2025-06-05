
import * as React from 'react';
import { Paper, Stack, Typography, CssBaseline, Box, ThemeProvider, createTheme } from '@mui/material';
import { JSX } from '@emotion/react/jsx-runtime';
import { DeviceTreeView } from './DeviceTreeView';
import { ErrorDisplay } from './ErrorDisplay';
import { UserList } from './UserList';
import { Login } from './Login';
import { getCsrfToken } from './RequestTools';
import { CountdownTimer } from './CountdownTimer';
import { SESSION_UPDATE_INTERVAL_MS } from './AdminSettings';
import { LoadingButton } from './LoadingButtonGroup';

/**
 * The main App component.
 *
 * The function component for this website that includes all other components.  
 * It Contains the header area and the device tree.  
 * Also contains the color mode / theme.  
 * 
 * @return The react component of the main app.
 */
export function App(): JSX.Element {

	const [currentErrorMessage, setCurrentErrorMessage] = React.useState<string>('');
	const [isErrorOpen, setIsErrorOpen] = React.useState<boolean>(false);

	const [remainingSessionTimeSeconds, setRemainingSessionTimeSeconds] = React.useState<number | undefined>(undefined);

	const lastPingRef = React.useRef<Date>(new Date());
	const lastUserInputRef = React.useRef<Date>(new Date());
	const intervalRef = React.useRef<NodeJS.Timeout | null>(null);
	const remainingSessionTimeSecondsRef = React.useRef<number | null>(null);

	function onLoginSuccess(): void {
		getRemainingSessionTime();
	}

	function updateSessionTime(remainingTimeSeconds: number): void {
		setRemainingSessionTimeSeconds(remainingTimeSeconds);
		remainingSessionTimeSecondsRef.current = remainingTimeSeconds;
	}

	async function displayError(message: string, returnToLoginPage: boolean = false): Promise<void> {
		if (isErrorOpen) {
			// close previous error if still open
			setIsErrorOpen(false);
		}
		if (returnToLoginPage) {
			updateSessionTime(0);
		}
		setCurrentErrorMessage(message);
		setIsErrorOpen(true);
	}

	async function logout(): Promise<void> {

		const response = await fetch('/api/logout/', {
			method: 'POST',
			credentials: 'include',
			mode: 'same-origin',	// prevents sending token to another website
			headers: {
				'X-CSRFToken': await getCsrfToken(),	// need the CSRF token for POST requests
				'Content-type': 'application/json; charset=UTF-8'
			},
		});

		if (!response.ok) {
			const responseData = await response.json();
			displayError(`${response.status} ${response.statusText}: ${responseData.detail}`);
		}
		else {
			updateSessionTime(0);
		}
	}

	async function getRemainingSessionTime(): Promise<void> {

		const response = await fetch('/api/get-session-expiry-date/', {
			method: 'GET',
			credentials: 'include',
			mode: 'same-origin',	// prevents sending token to another website
		});

		const responseData = await response.json();

		if (!response.ok) {
			if (response.status === 401) {
				updateSessionTime(0);
			} else {
				displayError(`${response.status} ${response.statusText}: ${responseData.detail}`);
			}
			return;
		}
		else {
			const sessionExpiryDate: Date = new Date(responseData.session_expiry_date);
			const remainingTimeSeconds = (sessionExpiryDate.getTime() - Date.now()) / 1000;
			updateSessionTime(remainingTimeSeconds);
		}
	}

	async function pingServer(): Promise<void> {

		if (remainingSessionTimeSecondsRef.current === 0) {
			return;
		}

		if (lastPingRef.current > lastUserInputRef.current) {
			return;
		}

		lastPingRef.current = new Date();
		getRemainingSessionTime();
	}

	async function onUserInput(): Promise<void> {
		lastUserInputRef.current = new Date();
	}

	React.useEffect(() => {

		getRemainingSessionTime();

		addEventListener("mousemove", onUserInput);
		addEventListener("mousedown", onUserInput);
		addEventListener("mouseup", onUserInput);
		addEventListener("keydown", onUserInput);
		addEventListener("keyup", onUserInput);
		addEventListener("scroll", onUserInput);
		addEventListener("resize", onUserInput);

		intervalRef.current = setInterval(pingServer, SESSION_UPDATE_INTERVAL_MS);

		return function (): void {
			if (intervalRef.current) {
				clearInterval(intervalRef.current);
			}
		};

		// TODO: remove, code for security checks
		// This is a test to see if API requests before authentication work
		// fetch('/api/gettree/', {
		// 	method: 'GET',
		// 	credentials: 'include',
		// 	mode: 'same-origin',
		// });

		// This is a test to see if API requests before authentication work
		// new EventSource('/api/events/', {
		// 	withCredentials: true
		// });
	}, []);

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
			<Paper elevation={1} sx={{ padding: '2rem', width: '100%' }}>
				<Typography variant='h2' sx={{ whiteSpace: 'nowrap' }}>
					Smartplug Dirigent
				</Typography>
			</Paper>

			<Box sx={{ padding: '1.5rem' }}>
				{remainingSessionTimeSeconds === undefined ? undefined :
					(
						remainingSessionTimeSeconds > 0 ?
							<Stack
								direction='row'
								justifyContent='space-between'
								spacing={'1rem'}
							>
								<DeviceTreeView displayError={displayError} />

								<Stack
									direction='column'
									justifyContent='top'
									spacing={'2rem'}
								>
									<Stack
										direction='row'
										sx={{ alignSelf: 'end', mr: '2rem' }}
									>
										<CountdownTimer
											initialTime={remainingSessionTimeSecondsRef.current ? remainingSessionTimeSecondsRef.current : 0}
											sx={{ mr: '1rem' }}
										/>
										<LoadingButton
											onClick={logout}
											variant='contained'
											sx={{ minWidth: 'fit-content' }}
										>
											sign out
										</LoadingButton>

									</Stack>

									<UserList displayError={displayError} />

								</Stack>

							</Stack>
							:
							<Login onLoginSuccess={onLoginSuccess} displayError={displayError} />
					)
				}
				{/* ErrorDisplay is placed here but will only be shown if isErrorOpen is set */}
				<ErrorDisplay
					message={currentErrorMessage}
					isErrorOpen={isErrorOpen}
					setIsErrorOpen={setIsErrorOpen}
				/>
			</Box>
		</ThemeProvider >
	);
}


