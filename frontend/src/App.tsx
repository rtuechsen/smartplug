
/******************************************************************************************
 * @packageDocumentation  App.tsx
 * 
 * # TODO
 ******************************************************************************************/

import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import CssBaseline from '@mui/material/CssBaseline';	// used to remove default padding of html body
import Box from '@mui/material/Box';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { JSX } from '@emotion/react/jsx-runtime';
import DeviceTreeView from './DeviceTreeView';
import Login from './components/Login'
import React from "react";

/**
 * Main App component.
 *
 * The app function component for this website that includes all other components.  
 * It Contains the header area and the device tree.  
 * Also contains the color mode / theme.  
 * 
 * @return the react component of the main app
 */
function App(): JSX.Element {
	const [isLoggedIn, setLoggedIn] = React.useState(false);
	const onLoginSuccess = () => {
		setLoggedIn(true)
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
					Shelly Dirigent
				</Typography>
			</Paper>
			<Box sx={{ padding: '1.5rem' }}>
				{isLoggedIn ? <DeviceTreeView /> : <Login callback={onLoginSuccess} />}
			</Box>
			<Box sx={{ padding: '1.5rem' }}>
				<DeviceTreeView />
			</Box>
		</ThemeProvider >
	);
}


export default App;
