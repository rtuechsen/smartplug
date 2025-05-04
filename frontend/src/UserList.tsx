
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

	const users = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven'];

	return (

		<Stack direction='column'>
			<Typography variant="h5" sx={{ paddingBottom: '1rem' }}>
				Active Users
			</Typography>
			<Paper sx={{ maxHeight: '30rem', padding: '1rem' }}>
				<List sx={{ minWidth: '15rem', maxHeight: '100%', overflow: 'auto' }}>
					{users.map((name) => (<UserListItem key={name} name={name} />))}
				</List>
			</Paper>
		</Stack >


	);
}

export default UserList;