
import { SvgIcon, Tooltip } from '@mui/material';
import IndeterminateCheckBoxIcon from '@mui/icons-material/IndeterminateCheckBox';
import WifiRoundedIcon from '@mui/icons-material/WifiRounded';
import WifiOffRoundedIcon from '@mui/icons-material/WifiOffRounded';
import { JSX } from '@emotion/react/jsx-runtime';


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
		tooltip = 'All devices in group are ';
	} else {
		tooltip = 'Device is ';
	}
	switch (isOn) {
		case true:
			tooltip += 'ON';
			icon = <SvgIcon>
				{/* credit: modified bolt icon from https://fonts.google.com/icons */}
				<svg
					xmlns='http://www.w3.org/2000/svg'
					viewBox='0 0 24 24'
					stroke='none'
					fill='currentColor'
				>
					<path
						d='M 10.55,18.2 15.725,12 h -4 L 12.45,6.3249994 7.8250003,13 H 11.3 Z M 9.0000003,15 H 5.9000002 q -0.6,0 -0.8875001,-0.5375 -0.2875,-0.5375 0.0625,-1.0375 L 12.55,2.6749993 q 0.25,-0.35 0.65,-0.4875 0.4,-0.1375 0.825,0.012499 0.425,0.15 0.625001,0.5249999 Q 14.85,3.0999988 14.8,3.5249987 L 14,9.9999989 h 3.875 q 0.650001,0 0.912501,0.5750001 0.262499,0.575 -0.1625,1.075 L 10.4,21.5 q -0.275,0.325 -0.6749997,0.425 -0.4000001,0.1 -0.775,-0.075 -0.3749999,-0.175 -0.5875,-0.5375 Q 8.1500002,20.95 8.2000002,20.525 Z M 11.775,12.25 Z'
					/>
				</svg>
			</SvgIcon>;
			break;
		case false:
			tooltip += 'OFF';
			icon = <SvgIcon>
				{/* credit: modified bolt icon from https://fonts.google.com/icons*/}
				<svg
					xmlns='http://www.w3.org/2000/svg'
					viewBox='0 0 24 24'
					stroke='none'
					fill='currentColor'
				>
					<path
						d='m 13.605468,2.1210942 c -0.137499,-0.00208 -0.272916,0.020573 -0.40625,0.066406 -0.266666,0.091667 -0.481771,0.2549486 -0.648437,0.4882812 L 9.9472653,6.417969 11.386719,7.8574222 12.449219,6.3242191 12.15625,8.6269532 17.05664,13.527344 18.625,11.650391 c 0.283332,-0.333332 0.337109,-0.69284 0.162109,-1.076172 C 18.612109,10.190886 18.308332,10 17.875,10 H 14 l 0.800781,-6.4746092 c 0.03333,-0.2833324 -0.01706,-0.5507814 -0.150391,-0.800781 -0.133333,-0.25 -0.341667,-0.4253906 -0.625,-0.5253906 -0.141666,-0.05 -0.282422,-0.076042 -0.419922,-0.078125 z M 2.78125,2.5058598 c -0.265201,5e-5 -0.5195258,0.105423 -0.7070313,0.2929685 -0.3904236,0.390507 -0.3904236,1.0235556 0,1.4140625 L 7.623047,9.761719 5.0742187,13.425782 c -0.2333328,0.333332 -0.2541663,0.678776 -0.0625,1.037109 C 5.2033848,14.821223 5.5003914,15 5.9003904,15 h 3.0996095 l -0.8007812,5.525391 c -0.033333,0.283333 0.022396,0.545443 0.1640624,0.787109 0.1416663,0.241666 0.3359379,0.420443 0.5859375,0.537109 0.2499994,0.116667 0.5087245,0.142839 0.7753908,0.07617 C 9.9912751,21.859115 10.217058,21.716666 10.40039,21.5 l 4.076172,-4.884765 4.572266,4.572265 c 0.390507,0.390424 1.023555,0.390424 1.414062,0 0.390425,-0.390507 0.390425,-1.023555 0,-1.414062 L 3.4882812,2.7988283 C 3.3007758,2.6112828 3.0464509,2.5058998 2.78125,2.5058598 Z M 9.066406,11.205078 10.861328,13 H 7.8242187 Z m 2.179688,2.179688 1.810546,1.810547 -2.505859,3.003906 z'
					/>
				</svg>
			</SvgIcon>;
			break;
		default:
			tooltip = 'Devices in group are partially on';
			icon = <IndeterminateCheckBoxIcon />;
			break;
	}

	return (
		<Tooltip title={tooltip}>
			{icon}
		</Tooltip>);
}


/**
 * A data structure to pass information to an AvailableIcon.  
 */
export interface AvailableIconProps {

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
export function AvailableIcon({ isAvailable, isGroup }: AvailableIconProps): JSX.Element {

	let tooltip: string;
	let icon: JSX.Element;
	if (isGroup) {
		tooltip = 'All devices in group are ';
	} else {
		tooltip = 'Device is ';
	}
	switch (isAvailable) {
		case true:
			tooltip += 'available';
			icon = <WifiRoundedIcon />;
			break;
		case false:
			tooltip += 'not available';
			icon = <WifiOffRoundedIcon />;
			break;
		default:
			tooltip = 'Devices in group are partially available';
			icon = <IndeterminateCheckBoxIcon />;
			break;
	}

	return (
		<Tooltip title={tooltip}>
			{icon}
		</Tooltip>);
}





