
import * as React from 'react';
import { JSX } from '@emotion/react/jsx-runtime';
import Typography from '@mui/material/Typography';


// TODO: remove trigger
interface CountdownTimerProps {
	initialTime: number;
	sx?: object;
}

// TODO: add source

function CountdownTimer({ initialTime, sx }: CountdownTimerProps): JSX.Element {

	const [remainingTime, setRemainingTime] = React.useState<number>(initialTime);
	const [timeString, setTimeString] = React.useState('');
	const intervalRef = React.useRef<NodeJS.Timeout | null>(null);

	React.useEffect(() => {
		setRemainingTime(initialTime);
		setTimeString(secondsToString(initialTime));

		if (intervalRef.current) {
			clearInterval(intervalRef.current);
		}
	}, [initialTime]);

	function secondsToString(remainingSeconds: number): string {
		const minutes = Math.floor(remainingSeconds / 60);
		const seconds = Math.floor(remainingSeconds % 60);
		return `${minutes < 10 ? '0' : ''}${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
	}

	function updateTimer(): void {
		let newRemainingTime = remainingTime - 1;
		if (newRemainingTime < 0) {
			newRemainingTime = 0;
			if (intervalRef.current) {
				clearInterval(intervalRef.current);
			}
		}
		setRemainingTime(newRemainingTime);
		setTimeString(secondsToString(newRemainingTime));
	}

	React.useEffect(() => {
		if (intervalRef.current) {
			clearInterval(intervalRef.current);
		}

		if (remainingTime > 0) {
			intervalRef.current = setInterval(updateTimer, 1000);
		}

		return function (): void {
			if (intervalRef.current) {
				clearInterval(intervalRef.current);
			}
		};
	}, [remainingTime]);

	return (
		<Typography sx={{ display: 'flex', alignItems: 'center', lineHeight: 1, whiteSpace: 'nowrap', ...sx }}>
			{timeString}
		</Typography>
	);
}

export default CountdownTimer;