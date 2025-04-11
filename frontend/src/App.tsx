
import { Component } from 'react';


const API_HOST = '/api';
let csrfToken: string = "";


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

type AppState = { testGet: string, testPost: string };

class App extends Component<{}, AppState> {

	state: AppState = {
		testGet: 'Nope',
		testPost: 'Nope',
	};

	async componentDidMount() {
		this.setState({
			testGet: await testRequest('GET'),
			testPost: await testRequest('POST'),
		});
	}

	render() {
		return (
			<div>
				<p>Test GET request: {this.state.testGet}</p>
				<p>Test POST request: {this.state.testPost}</p>
			</div>
		);
	}
}


export default App
