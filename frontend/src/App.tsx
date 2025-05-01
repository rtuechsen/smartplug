
import * as React from 'react';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { JSX } from '@emotion/react/jsx-runtime';
import DeviceTreeView from './DeviceTreeView';
import ErrorDisplay from './ErrorDisplay';


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

	const [currentErrorMessage, setCurrentErrorMessage] = React.useState<string>('');
	const [isErrorOpen, setIsErrorOpen] = React.useState<boolean>(false);

	async function displayError(message: string): Promise<void> {
		if (isErrorOpen) {
			// close previous error if still open
			// TODO: check if this works properly
			setIsErrorOpen(false);
		}
		setCurrentErrorMessage(message);
		setIsErrorOpen(true);
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
				<Typography variant="h2">
					Smartplug Dirigent
				</Typography>
			</Paper>
			<Box sx={{ padding: '1.5rem' }}>
				<DeviceTreeView displayError={displayError} />
				{/* ErrorDisplay is placed here but will only be shown if isErrorOpen is set */}
				<ErrorDisplay message={currentErrorMessage} isErrorOpen={isErrorOpen} setIsErrorOpen={setIsErrorOpen} />
			</Box>
		</ThemeProvider >
	);
}


export default App;
