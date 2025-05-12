
/**
 * The CSRF token - needed to prevent CSRF. 
 *
 * Required for making requests to the API (except GET requests). Token is provided by the API itself.
 */
let csrfToken: string = '';


/**
 * A function that requests a CSRF token from the API.
 *
 * Requests the token when first called and simply returns the token on
 * subsequent calls.
 * 
 * @return The CSRF token.
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





