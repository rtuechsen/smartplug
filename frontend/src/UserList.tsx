import * as React from "react";
import {
	List,
	ListItem,
	ListItemText,
	ListItemAvatar,
	Avatar,
	Typography,
	Stack,
	Paper,
} from "@mui/material";
import { JSX } from "@emotion/react/jsx-runtime";
import { DisplayErrorCallbackProps } from "./ErrorDisplay";

/**
 * A data structure to hold the username for the user list item.
 */
interface UserListItemProps {
	/**
	 * The username to display.
	 */
	name: string;
}

/**
 * A list item that displays a username which can be added to a List (Material UI) component.
 *
 * @param props Holds the data needed to construct the error display.
 *
 * @returns The react component of the user list item.
 */
function UserListItem({ name }: UserListItemProps): JSX.Element {
	return (
		<ListItem sx={{ padding: "0.5rem" }}>
			<ListItemAvatar sx={{ minWidth: "0rem", paddingRight: "0.7rem" }}>
				<Avatar sx={{ width: "2rem", height: "2rem" }}>
					{name[0]}
				</Avatar>
			</ListItemAvatar>
			<ListItemText primary={name} />
		</ListItem>
	);
}

/**
 * A list which displays the usernames of the currently loggin in users.
 *
 * @param props Holds the data needed to construct the user list.
 *
 * @returns The react component of the user list.
 */
export function UserList({
	displayError,
}: DisplayErrorCallbackProps): JSX.Element | undefined {
	// state for holding the data of the tree, triggers updates to the tree if the data changes
	const [userListState, setUserListState] = React.useState<string[]>();

	React.useEffect(() => {
		// declare an async function to fetch and process the data
		async function getUserList(): Promise<void> {
			// fetch the tree data
			const response = await fetch("/api/get-active-users/", {
				method: "GET",
				credentials: "include",
				mode: "same-origin", // prevents sending token to another website
			});

			const userList = await response.json();

			// set the state with it to trigger the tree to update
			setUserListState(userList);
		}

		// start the async function, don't wait for it to finish
		getUserList();

		// create the event source for SSE
		const eventSource = new EventSource("/api/events/", {
			withCredentials: true,
		});

		eventSource.addEventListener("user_list_update", (event) => {
			const userData = JSON.parse(event.data) as string[];
			setUserListState(userData);
		});

		eventSource.onerror = function (): void {
			displayError(
				"ERROR: You either lost connection to the server or your session expired.",
				true,
			);
		};

		return function (): void {
			// need to close EventSource to avoid subscribing twice in StrictMode (in StrictMode components will
			// be mounted multiple times to detect side effects, see main.tsx)

			eventSource.close();
		};
	}, []); // empty dependencies => will only run once after component mounted

	return userListState == undefined ? undefined : (
		<Stack direction="column">
			<Typography
				variant="h5"
				sx={{ paddingBottom: "1rem", paddingLeft: "1rem" }}
			>
				Active Users
			</Typography>
			<Paper sx={{ maxHeight: "30rem", padding: "0.7rem" }}>
				<List
					sx={{
						minWidth: "15rem",
						maxWidth: "25rem",
						maxHeight: "100%",
						overflow: "auto",
						padding: "0rem",
					}}
				>
					{userListState.map((name) => (
						<UserListItem key={name} name={name} />
					))}
				</List>
			</Paper>
		</Stack>
	);
}
