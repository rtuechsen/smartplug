import { Tooltip } from "@mui/material";
import IndeterminateCheckBoxIcon from "@mui/icons-material/IndeterminateCheckBox";
import WifiRoundedIcon from "@mui/icons-material/WifiRounded";
import WifiOffRoundedIcon from "@mui/icons-material/WifiOffRounded";
import FlashOnRoundedIcon from "@mui/icons-material/FlashOnRounded";
import FlashOffRoundedIcon from "@mui/icons-material/FlashOffRounded";
import { JSX } from "@emotion/react/jsx-runtime";

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
		tooltip = "All devices in group are ";
	} else {
		tooltip = "Device is ";
	}
	switch (isOn) {
		case true:
			tooltip += "ON";
			icon = <FlashOnRoundedIcon />;
			break;
		case false:
			tooltip += "OFF";
			icon = <FlashOffRoundedIcon />;
			break;
		default:
			tooltip = "Devices in group are partially on";
			icon = <IndeterminateCheckBoxIcon />;
			break;
	}

	return <Tooltip title={tooltip}>{icon}</Tooltip>;
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
export function AvailableIcon({
	isAvailable,
	isGroup,
}: AvailableIconProps): JSX.Element {
	let tooltip: string;
	let icon: JSX.Element;
	if (isGroup) {
		tooltip = "All devices in group are ";
	} else {
		tooltip = "Device is ";
	}
	switch (isAvailable) {
		case true:
			tooltip += "available";
			icon = <WifiRoundedIcon />;
			break;
		case false:
			tooltip += "not available";
			icon = <WifiOffRoundedIcon />;
			break;
		default:
			tooltip = "Devices in group are partially available";
			icon = <IndeterminateCheckBoxIcon />;
			break;
	}

	return <Tooltip title={tooltip}>{icon}</Tooltip>;
}
