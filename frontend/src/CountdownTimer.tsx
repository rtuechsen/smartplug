
import * as React from 'react';
import { JSX } from '@emotion/react/jsx-runtime';


interface CountdownTimerProps {
	// resetTimeSecondsRef: React.Ref<number>;
	initialTime: number;
	trigger: boolean;
}

function CountdownTimer({ initialTime, trigger }: CountdownTimerProps): JSX.Element {

	// const remainingTimeSecondsRef = React.useRef<number>(resetTimeSecondsRef?.current);
	const [remainingTime, setRemainingTime] = React.useState<number>(initialTime);
	const [timeString, setTimeString] = React.useState('');
	const intervalRef = React.useRef<NodeJS.Timeout | null>(null);

	React.useEffect(() => {
		// remainingTimeSecondsRef.current = resetTimeSecondsRef.current;
		// setRemainingTime(resetTimeSecondsRef?.current);
		setRemainingTime(initialTime);
		setTimeString(secondsToString(initialTime));

		if (intervalRef.current) {
			clearInterval(intervalRef.current);
		}
	}, [initialTime, trigger]);

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
		<div>
			{timeString}
		</div>
	);
}

export default CountdownTimer;