
/**
 * The CSRF token
 *
 * Needed for requests to the API (except GET requests). Only fetched once. 
 */
let csrfToken: string = '';


/**
 * A function that requests a CSRF token from the API
 *
 * Requests the token when first called and simply returns the token on
 * subsequent calls.
 * 
 * @return the CSRF token
 */
export async function getCsrfToken(): Promise<string> {
	if (csrfToken === '') {
		const response = await fetch('/api/csrf/', {
			credentials: 'include',
		});
		const data = await response.json();
		csrfToken = data.csrfToken;
	}
	return csrfToken;
}





