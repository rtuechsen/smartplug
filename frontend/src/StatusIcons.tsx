
import WifiOffOutlinedIcon from '@mui/icons-material/WifiOffOutlined';
import WifiOutlinedIcon from '@mui/icons-material/WifiOutlined';
import PowerOffOutlinedIcon from '@mui/icons-material/PowerOffOutlined';
import PowerOutlinedIcon from '@mui/icons-material/PowerOutlined';
import HelpOutlineOutlinedIcon from '@mui/icons-material/HelpOutlineOutlined';
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
