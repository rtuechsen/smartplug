
import * as React from 'react';
import { ButtonGroup, Button } from '@mui/material';
import type { OverridableStringUnion } from '@mui/types';
import type { ButtonPropsVariantOverrides } from '@mui/material/Button';
import { JSX } from '@emotion/react/jsx-runtime';


/**
 * A data structure to pass information to an LoadingButton.  
 */
export interface LoadingButtonProps {

	/**
	 * The (async) callback used when clicking the button. 
	 * 
	 * @returns A void Promise that can be waited on if one wants to wait for the function to complete.
	 */
	onClick: () => Promise<void>;
	variant?: OverridableStringUnion<'text' | 'outlined' | 'contained', ButtonPropsVariantOverrides>;
	sx?: object;
	ref?: React.Ref<HTMLButtonElement>;
}


/**
 * A button that shows a loading circle while waiting for its callback to finish.  
 * 
 * @param props The properties needed to construct the button.
 * 
 * @return The react component of the button.
 */
export function LoadingButton({ onClick, variant, children, sx, ref }: React.PropsWithChildren<LoadingButtonProps>): JSX.Element {

	// state that decides wheter to show a loading circle or not, triggers the button to update when state changes
	const [loading, setLoading] = React.useState<boolean>(false);

	/**
	 * Wrapper function to wrap the callback of the button between changes to the loading state.
	 * 
	 * @return A void Promise that can be waited on if one wants to wait for the function to complete.
	 */
	async function handleClick(): Promise<void> {
		setLoading(true);
		await onClick();
		setLoading(false);
	}

	return (
		<Button
			onClick={handleClick}
			loading={loading}
			sx={{ whiteSpace: 'nowrap', ...sx }}
			variant={variant || 'text'}
			ref={ref}
		>
			{children}
		</Button>
	);
}


/**
 * A data structure to pass information to an LoadingButtonGroup.  
 */
export interface LoadingButtonGroupProps {

	onClickLeftButton: () => Promise<void>;
	onClickRightButton: () => Promise<void>;
	buttonLabelLeft: string;
	buttonLabelRight: string;
}


/**
 * A combined group of 'ON' and 'OFF' button which each show a loading circle while waiting for its callback to finish.
 *
 * @param props Holds the data needed to construct the button.
 * 
 * @return The react component of the button group.
 */
export function LoadingButtonGroup({ onClickLeftButton, onClickRightButton, buttonLabelLeft, buttonLabelRight }: LoadingButtonGroupProps): JSX.Element {

	return (
		<ButtonGroup size='small'>
			<LoadingButton onClick={onClickLeftButton} variant='outlined'>{buttonLabelLeft}</LoadingButton>
			<LoadingButton onClick={onClickRightButton} variant='outlined'>{buttonLabelRight}</LoadingButton>
		</ButtonGroup>
	);
}
