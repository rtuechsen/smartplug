import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
	// using StrictMode results in double API calls in development, this does not happen in production builds
	<StrictMode>
		<App />
	</StrictMode>,
)
