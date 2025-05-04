
import * as React from 'react';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import Avatar from '@mui/material/Avatar';
import Typography from '@mui/material/Typography';
import Stack from '@mui/material/Stack';
import Paper from '@mui/material/Paper';
import PersonRoundedIcon from '@mui/icons-material/PersonRounded';
import { JSX } from '@emotion/react/jsx-runtime';


interface UserListItemProps {
	name: string;
}


function UserListItem({ name }: UserListItemProps): JSX.Element {
	return (
		<ListItem>
			<ListItemAvatar>
				<Avatar>
					<PersonRoundedIcon />
				</Avatar>
			</ListItemAvatar>
			<ListItemText primary={name} />
		</ListItem>
	);
}


function UserList(): JSX.Element {

	// const userList = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven'];

	// state for holding the data of the tree, triggers updates to the tree if the data changes
	const [userListState, setUserListState] = React.useState<string[]>();

	// explanation: see DeviceTreeView
	// const [userListDataArrivedState, setUserListDataArrivedState] = React.useState<boolean>(false);

	React.useEffect(() => {

		// declare an async function to fetch and process the data
		async function getUserList(): Promise<void> {

			// fetch the tree data
			const response = await fetch('/api/getusers/', {
				method: 'GET',
				credentials: 'include',
				mode: 'same-origin',	// prevents sending token to another website
			});

			const userList = await response.json();

			// TODO: error display
			// if (!response.ok) {
			// 	displayError(`${response.status} ${response.statusText}: ${responseData.message}`);
			// 	// abort tree view creation
			// 	return;
			// }

			// set the state with it to trigger the tree to update
			setUserListState(userList);

			// set the state bool to trigger useLayoutEffect()
			// setUserListDataArrivedState(true);
		}

		// start the async function, don't wait for it to finish
		getUserList();

		// create the event source for SSE
		// const eventSource = new EventSource('/api/events/', {
		// 	withCredentials: true
		// });
		// TODO: can this fail? error handling!

		// register a function to run when a SSE message arrives, converts the update to the tree view
		// from JSON to interface and updates the state to trigger the tree to update
		// eventSource.onmessage = function (event): void {
		// 	const userData = JSON.parse(event.data);
		// 	setUserListState(userData);
		// };

		// TODO: error handling
		// eventSource.onerror = function (): void {
		// 	displayError('Server Sent Events (SSE) have failed.');
		// };

		// return function (): void {

		// 	// need to close EventSource to avoid subscribing twice in StrictMode (in StrictMode components will
		// 	// be mounted multiple times to detect side effects, see main.tsx)

		// 	eventSource.close();
		// };

	}, []);	// empty dependencies => will only run once after component mounted

	return (
		userListState == undefined ? null :
			<Stack direction='column'>
				<Typography variant="h5" sx={{ paddingBottom: '1rem', paddingLeft: '1rem' }}>
					Active Users
				</Typography>
				<Paper sx={{ maxHeight: '30rem', padding: '1rem' }}>
					<List sx={{ minWidth: '15rem', maxHeight: '100%', overflow: 'auto', padding: '0rem' }}>
						{userListState.map((name) => (<UserListItem key={name} name={name} />))}
					</List>
				</Paper>
			</Stack >
	);
}

export default UserList;