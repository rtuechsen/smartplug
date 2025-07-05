
import * as React from 'react';
import { Typography } from '@mui/material';
import { JSX } from '@emotion/react/jsx-runtime';


/**
 * A Data structure to pass information to the countdown timer.
 */
export interface CountdownTimerProps {

	/**
	 * The initial time to start with in seconds.
	 */
	initialTimeSeconds: number;

	/**
	 * An object of optional css stylings options to pass to the text component of the countdown timer.
	 */
	sx?: object;
}

/**
 * A countdown timer that displays the minutes and seconds and counts down to zero.
 * 
 * Implementationed based roughly on: https://www.freecodecamp.org/news/build-a-countdown-timer-with-react-step-by-step/
 * 
 * @param props Holds the data needed to construct the countdown timer.
 * 
 * @returns The react component of the countdown timer.
 */
export function CountdownTimer({ initialTimeSeconds, sx }: CountdownTimerProps): JSX.Element {

	const [remainingTimeSeconds, setRemainingTimeSeconds] = React.useState<number>(initialTimeSeconds);
	const [timeString, setTimeString] = React.useState('');
	const intervalRef = React.useRef<NodeJS.Timeout | null>(null);

	React.useEffect(() => {
		setRemainingTimeSeconds(initialTimeSeconds);
		setTimeString(secondsToString(initialTimeSeconds));

		if (intervalRef.current) {
			clearInterval(intervalRef.current);
		}
	}, [initialTimeSeconds]);

	function secondsToString(remainingSeconds: number): string {
		const minutes = Math.floor(remainingSeconds / 60);
		const seconds = Math.floor(remainingSeconds % 60);
		return `${minutes < 10 ? '0' : ''}${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
	}

	function updateTimer(): void {
		let newRemainingTime = remainingTimeSeconds - 1;
		if (newRemainingTime < 0) {
			newRemainingTime = 0;
			if (intervalRef.current) {
				clearInterval(intervalRef.current);
			}
		}
		setRemainingTimeSeconds(newRemainingTime);
		setTimeString(secondsToString(newRemainingTime));
	}

	React.useEffect(() => {
		if (intervalRef.current) {
			clearInterval(intervalRef.current);
		}
		// TODO 1000 Magic Number explain 
		if (remainingTimeSeconds > 0) {
			intervalRef.current = setInterval(updateTimer, 1000);
		}

		return function (): void {
			if (intervalRef.current) {
				clearInterval(intervalRef.current);
			}
		};
	}, [remainingTimeSeconds]);

	return (
		<Typography sx={{ display: 'flex', alignItems: 'center', lineHeight: 1, whiteSpace: 'nowrap', ...sx }}>
			{timeString}
		</Typography>
	);
}
