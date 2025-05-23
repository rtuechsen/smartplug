
/**
 * The CSRF token - needed to prevent CSRF. 
 *
 * Required for making requests to the API (except GET requests). Token is provided by the API itself.
 */
// let csrfToken: string = '';


/**
 * A function that requests a CSRF token from the API.
 *
 * Requests the token when first called and simply returns the token on
 * subsequent calls.
 * 
 * @return The CSRF token.
 */
export async function getCsrfToken(): Promise<string> {
	// if (csrfToken === '') {
	// 	const response = await fetch('/api/csrf/', {
	// 		method: 'GET',
	// 		credentials: 'include',
	// 		mode: 'same-origin',	// prevents sending token to another website
	// 	});
	// 	const data = await response.json();
	// 	csrfToken = data.csrfToken;
	// }
	return csrfToken;
}

// https://docs.djangoproject.com/en/5.2/howto/csrf/#acquiring-the-token-if-csrf-use-sessions-and-csrf-cookie-httponly-are-false
function getCookie(name): string {
	let cookieValue = null;
	if (document.cookie && document.cookie !== '') {
		const cookies = document.cookie.split(';');
		for (let i = 0; i < cookies.length; i++) {
			const cookie = cookies[i].trim();
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) === (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}
export const csrfToken = getCookie('csrftoken');




