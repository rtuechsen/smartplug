
import WifiOffOutlinedIcon from '@mui/icons-material/WifiOffOutlined';
import WifiOutlinedIcon from '@mui/icons-material/WifiOutlined';
import PowerOffOutlinedIcon from '@mui/icons-material/PowerOffOutlined';
import PowerOutlinedIcon from '@mui/icons-material/PowerOutlined';
import HelpOutlineOutlinedIcon from '@mui/icons-material/HelpOutlineOutlined';
import SvgIcon from '@mui/material/SvgIcon';
import Tooltip from '@mui/material/Tooltip';
import { JSX } from '@emotion/react/jsx-runtime';

// TODO: de-duplicate these two components ???

/**
 * A data structure to pass information to an OnIcon.  
 */
export interface OnIconProps {

	/**
	 * A boolean indicating if the item should be turned on (True) or off (False). 
	 */
	isOn: boolean;

	/**
	 * If the item is a group or a device.
	 */
	isGroup: boolean;
}


/**
 * A component for an icon with different states and a tooltip to inform about the isOn state of an tree item.  
 *
 * Switches between tree icons on if the item is on or not. Groups can have a mixed state 
 * as well if their children have different values.  
 * 
 * @param props Holds the data needed to construct the icon.
 * 
 * @return The react component of the icon.
 */
export function OnIcon({ isOn, isGroup }: OnIconProps): JSX.Element {

	let tooltip: string;
	let icon: JSX.Element;
	if (isGroup) {
		tooltip = 'All devices in Group are ';
	} else {
		tooltip = 'Device is ';
	}
	switch (isOn) {
		case true:
			tooltip += 'on';
			icon = <PowerOutlinedIcon />;
			break;
		case false:
			tooltip += 'off';
			icon = <PowerOffOutlinedIcon />;
			break;
		default:
			tooltip = 'Devices in Group are partially on';
			icon = <HelpOutlineOutlinedIcon />;
			break;
	}

	return (
		<Tooltip title={tooltip}>
			{icon}
		</Tooltip>);
}


/**
 * A data structure to pass information to an AvilableIcon.  
 */
export interface AvilableIconProps {

	/**
	 * A boolean indicating if the item is currently reachable.
	 */
	isAvailable: boolean;

	/**
	 * If the item is a group or a device.
	 */
	isGroup: boolean;
}


/**
 * A component for an icon with different states and tooltip to inform about the isAvailable state of an tree item.  
 *
 * Switches between tree icons on if the item is available or not. Groups can have a mixed state 
 * as well if their children have different values.  
 * 
 * @param props Holds the data needed to construct the icon.
 * 
 * @return The react component of the icon.
 */
export function AvilableIcon({ isAvailable, isGroup }: AvilableIconProps): JSX.Element {

	let tooltip: string;
	let icon: JSX.Element;
	if (isGroup) {
		tooltip = 'All devices in Group are ';
	} else {
		tooltip = 'Device is ';
	}
	switch (isAvailable) {
		case true:
			tooltip += 'available';
			icon = <WifiOutlinedIcon />;
			break;
		case false:
			tooltip += 'not available';
			icon = <WifiOffOutlinedIcon />;
			break;
		default:
			tooltip = 'Devices in Group are partially available';
			icon = <HelpOutlineOutlinedIcon />;
			break;
	}

	return (
		<Tooltip title={tooltip}>
			{icon}
		</Tooltip>);
}


export function WifiIcon({ isAvailable, isGroup }: AvilableIconProps): JSX.Element {
	return (
		<SvgIcon>
			{/* credit: modified wifi icon from https://fonts.google.com/icons*/}
			<svg
				xmlns="http://www.w3.org/2000/svg"
				fill="currentColor"
				viewBox="0 0 24 24"
				stroke="none"
			>
				{isAvailable === true ? <path
					d="M 12,4 C 8.1672317,4 4.4897192,5.5305712 1.7812496,8.25 c -0.5840198,0.5873766 -0.581397,1.536953 0.00586,2.121094 0.5873876,0.584008 1.5369641,0.581408 2.1210937,-0.0059 C 6.0560187,8.2087676 8.9649417,7 12,7 c 3.035058,0 5.94398,1.2087275 8.091797,3.365234 0.584129,0.587268 1.533706,0.589868 2.121094,0.0059 C 22.800173,9.7869482 22.802796,8.8373809 22.21875,8.25 19.510281,5.5305713 15.832768,4 12,4 Z"
				/> : null}
				{isAvailable !== false ? <path
					d="m 12,10.5 c -2.1243431,0 -4.1628688,0.842255 -5.6660156,2.341797 -0.5867161,0.584679 -0.5884629,1.534254 -0.00391,2.121094 0.5852076,0.586187 1.5347818,0.587035 2.1210938,0.002 C 9.3918574,14.026371 10.668248,13.5 12,13.5 c 1.331752,0 2.608146,0.526418 3.548828,1.464844 0.586313,0.585083 1.535886,0.584234 2.121094,-0.002 0.584559,-0.586837 0.582807,-1.536412 -0.0039,-2.121094 C 16.162862,11.342302 14.124343,10.5 12,10.5 Z"
				/> : null}
				<path
					d="m 12,17 c -0.828425,0 -1.5,0.671575 -1.5,1.5 0,0.828425 0.671575,1.5 1.5,1.5 0.828425,0 1.5,-0.671575 1.5,-1.5 C 13.5,17.671575 12.828425,17 12,17 Z"
				/>
			</svg>
		</SvgIcon>
	);
}

export function BoltIcon({ isOn, isGroup }: OnIconProps): JSX.Element {
	return (
		<SvgIcon>
			{/* credit: modified bolt icon from https://fonts.google.com/icons*/}
			<svg
				xmlns="http://www.w3.org/2000/svg"

				viewBox="0 0 24 24"
				stroke="none"
			>
				{isOn === true ? <path
					fill="orange"
					d="M 13.582354,3.3756636 6.3925781,13.75 h 4.0429689 l -1.0058595,6.962891 v 0 L 17.328125,11.25 h -4.751953 z"
				/> : null}
				{isOn == null ? <path
					fill="darkred"
					d="M 7.2578125 12.5 L 6.3925781 13.75 L 10.435547 13.75 L 9.4296875 20.712891 L 16.285156 12.5 L 7.2578125 12.5 z "
				/> : null}
				<path
					fill="currentColor"
					d="M 10.55,18.2 15.725,12 h -4 L 12.45,6.3249994 7.8250003,13 H 11.3 Z M 9.0000003,15 H 5.9000002 q -0.6,0 -0.8875001,-0.5375 -0.2875,-0.5375 0.0625,-1.0375 L 12.55,2.6749993 q 0.25,-0.35 0.65,-0.4875 0.4,-0.1375 0.825,0.012499 0.425,0.15 0.625001,0.5249999 Q 14.85,3.0999988 14.8,3.5249987 L 14,9.9999989 h 3.875 q 0.650001,0 0.912501,0.5750001 0.262499,0.575 -0.1625,1.075 L 10.4,21.5 q -0.275,0.325 -0.6749997,0.425 -0.4000001,0.1 -0.775,-0.075 -0.3749999,-0.175 -0.5875,-0.5375 Q 8.1500002,20.95 8.2000002,20.525 Z M 11.775,12.25 Z"
				/>
			</svg>
		</SvgIcon>
	);
}
