
import * as React from 'react';
import Button from '@mui/material/Button';


const API_HOST = '/api';
let csrfToken: string = "";


const eventSource = new EventSource(`${API_HOST}/events/`, {
	withCredentials: true
});

eventSource.onmessage = function (event) {
	console.log('Received SSE:', event.data);
};


async function getCsrfToken() {
	if (csrfToken === "") {
		const response = await fetch(`${API_HOST}/csrf/`, {
			credentials: 'include',
		});
		const data = await response.json();
		csrfToken = data.csrfToken;
	}
	return csrfToken;
}


async function testRequest(method: string) {
	const response = await fetch(`${API_HOST}/ping/`, {
		method: method,
		// don't send CSRF token for GET requests, only for modifying requests
		headers: (
			method === 'POST'
				? { 'X-CSRFToken': await getCsrfToken() }
				: {}
		),
		credentials: 'include',
		mode: 'same-origin',	// prevents sending token to another website
	});
	const data = await response.json();
	return data.result;
}


async function getDeviceTree() {
	const response = await fetch(`${API_HOST}/gettree/`, {
		method: 'GET',
		credentials: 'include',
		mode: 'same-origin',	// prevents sending token to another website
	});
	const data = await response.json();
	return data;
}


type AppState = { testGet: string, testPost: string, testGetTree: string };

class App extends React.Component<{}, AppState> {

	state: AppState = {
		testGet: 'Nope',
		testPost: 'Nope',
		testGetTree: 'no tree received yet'
	};

	async componentDidMount() {
		this.setState({
			testGet: await testRequest('GET'),
			testPost: await testRequest('POST'),
			testGetTree: JSON.stringify(await getDeviceTree()),
		});
	}

	render() {
		return (
			<div>
				<p>Test GET request: {this.state.testGet}</p>
				<p>Test POST request: {this.state.testPost}</p>
				<p>Test gettree request: {this.state.testGetTree}</p>
				<Button
					onClick={async () => {
						const id: string = 'f7f7a115bea9310b163934fb414de46009662610454c78a3a9bb2b823cc4aafb';
						fetch(`${API_HOST}/switch/`, {
							method: 'POST',
							headers: {
								'X-CSRFToken': await getCsrfToken(),
								'Content-type': 'application/json; charset=UTF-8'
							},
							credentials: 'include',
							mode: 'same-origin',	// prevents sending token to another website
							body: JSON.stringify({
								id: id,
								isOn: true
							}),
						});
					}}
				>
					Switch On
				</Button>

			</div>
		);
	}
}


export default App
