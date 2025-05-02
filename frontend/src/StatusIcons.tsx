
import WifiOffOutlinedIcon from '@mui/icons-material/WifiOffOutlined';
import WifiOutlinedIcon from '@mui/icons-material/WifiOutlined';
import PowerOffOutlinedIcon from '@mui/icons-material/PowerOffOutlined';
import PowerOutlinedIcon from '@mui/icons-material/PowerOutlined';
import HelpOutlineOutlinedIcon from '@mui/icons-material/HelpOutlineOutlined';
import SignalWifiStatusbar4BarRoundedIcon from '@mui/icons-material/SignalWifiStatusbar4BarRounded';
import SignalWifi0BarRoundedIcon from '@mui/icons-material/SignalWifi0BarRounded';
import NetworkWifi2BarRoundedIcon from '@mui/icons-material/NetworkWifi2BarRounded';
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
			icon = <SignalWifiStatusbar4BarRoundedIcon />;
			break;
		case false:
			tooltip += 'not available';
			icon = <SignalWifi0BarRoundedIcon />;
			break;
		default:
			tooltip = 'Devices in Group are partially available';
			icon = <NetworkWifi2BarRoundedIcon />;
			break;
	}

	return (
		<Tooltip title={tooltip}>
			{icon}
		</Tooltip>);
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
					fill="red"
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
