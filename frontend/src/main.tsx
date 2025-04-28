
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';


createRoot(document.getElementById('root')!).render(
	/**
	 * using StrictMode results in components being mounted multiple times (and API called multiple times)
	 * to detect side effects.
	 * This only happens for development builds, not in production builds.
	 */
	<StrictMode>
		<App />
	</StrictMode>,
);
