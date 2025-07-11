"""Contains the MQTT client which serves as a central interface for all
communication (with the smartplugs) via MQTT."""

import json
from typing import Callable
import paho.mqtt.client as mqtt
from .logger import Logger
from .error_handler import BackendError
from .admin_settings import USE_MQTT


class MQTTClient:
    """MQTTClient handles MQTT communication for device status updates and
    control.

    It listens to topics, parses incoming messages, and sends control
    messages.
    """

    def __init__(
        self, on_update_callback: Callable[[str, str, bool], None]
    ) -> None:
        """Initialize the MQTT client and set up connection and callbacks.

        @param on_update_callback Callback function to update device states in
        the main application.
        """

        self._logger: Logger = Logger()

        self._broker_ip: str = "localhost"
        self._broker_port: int = 1883
        self._keep_alive_seconds: float = 60
        self._sub_topic: str = "/rpc"
        self._client: mqtt.Client = mqtt.Client()

        # After every install you must update the mosquitto_passwd.json

        path_to_username_password: str = "/etc/mosquitto/mosquitto_passwd.json"
        try:
            with open(path_to_username_password, "r", encoding="UTF-8") as f:
                config = json.load(f)
                self._username = config["mqtt_username"]
                self._password = config["mqtt_password"]
        except FileNotFoundError as e:
            raise BackendError(
                f"Could not find the file mosquitto_passwd.json at "
                f"{path_to_username_password}."
            ) from e
        except IOError as e:
            raise BackendError(
                f"Error while reading the file mosquitto_passwd.json at "
                f"{path_to_username_password}."
            ) from e
        except json.JSONDecodeError as e:
            raise BackendError(
                f"Error while parsing mosquitto_passwd.json:{e}."
            ) from e

        # TLS --------------------------------------
        # TODO: generate / add certificates when installing / starting
        # or add them to git and copy them when installing / starting

        # self._client.tls_set(
        #     ca_certs="/var/lib/mosquitto/ssl/server.crt",
        #     certfile="/home/admin/shelly-dirigent/backend/certs/client.crt",
        #     keyfile="/home/admin/shelly-dirigent/backend/certs/client.key",
        # )

        # self._client.tls_insecure_set(True)
        # -------------------------------------------

        self._client.username_pw_set(self._username, self._password)

        self._connect()
        self._on_update_callback: Callable[[str, str, bool], None] = (
            on_update_callback
        )
        self._client.on_message = self._on_message
        self._client.loop_start()

    def _connect(self) -> None:
        """Connects to the MQTT broker and subscribes to all topics."""

        def on_connect(client: mqtt.Client, userdata, flags, rc: int):
            if rc == 0:
                client.subscribe("#")
                self._logger.info("Connected successfully to MQTT broker.")
            else:
                raise BackendError("Failed to connect to MQTT broker.")

        self._client.on_connect = on_connect
        self._client.connect(
            self._broker_ip, self._broker_port, self._keep_alive_seconds
        )

    def _on_message(
        self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage
    ) -> None:
        """Processes incomming MQTT messages and triggers the update callback.

        Extracts device ID and state information from the topic and payload.

        @param client The instance of mqtt.Client to use.

        @param userdata Additional user data, not used here.

        @param msg The received message.
        """

        topic = msg.topic
        payload = msg.payload.decode()

        # Handles a message when the topic end swith "/online" indicating the
        # availability.
        if topic.endswith("/online"):
            deviceId = topic.split("/")[0]
            state = payload.strip().lower() == "true"

            # Notify the application about device availibilty
            self._on_update_callback(deviceId, "isAvailable", state)
            if state:
                # If device is online, request its current status
                self._request_status(deviceId)
            else:
                # If device is offline, assume switch is off
                self._on_update_callback(deviceId, "isOn", False)

        # Handle messages when topic ends with "/status/switch:0" indicating
        # switch status update.
        elif topic.endswith("/status/switch:0"):
            deviceId = topic.split("/")[0]
            try:
                data = json.loads(payload)
                # Get the switch output state (True or False)
                rpc_switch_output = data.get("output")

                # Notify the application about the switch status
                self._on_update_callback(deviceId, "isOn", rpc_switch_output)

            except json.JSONDecodeError as e:
                raise BackendError(
                    f"MQTT client received an invalid JSON for topic "
                    f"{topic}: {payload}"
                ) from e

        # Handle messages when the topic ends with "/rpc" indicating an RPC
        # response.
        elif topic.endswith("/rpc"):
            deviceId = topic.split("/")[0]
            try:
                data = json.loads(payload)
                deviceId = data.get("src")
                rpc_response = data.get("result")

                # Check if RPC result contains the Information of the switch
                # status.
                if isinstance(rpc_response, dict) and "output" in rpc_response:
                    output = rpc_response.get("output")

                    # Notify the application about the switch status
                    self._on_update_callback(deviceId, "isOn", output)

            except json.JSONDecodeError as e:
                self._logger.error(
                    f"[{topic}] Invalid JSON payload: {payload}"
                )
                raise BackendError(
                    f"Invalid JSON for topic {topic}: {payload}"
                ) from e
            except Exception as e:
                self._logger.error(f"Unexpeted error processing message: {e}")
                raise BackendError(f"Error in _on_message: {str(e)}") from e

    def _request_status(self, device_id: str) -> None:
        """Sends a Switch.GetStatus RPC request to a specific device.

        This requests the current switch status (ON/OFF) from the device.

        @param device_id The ID of the target device.
        """
        payload = {
            "id": 1,
            "src": "shelly",
            "method": "Switch.GetStatus",
            "params": {"id": 0},
        }
        # Publish the request to the device's RPC topic
        self._client.publish(device_id + self._sub_topic, json.dumps(payload))

    def disconnect(self) -> None:
        """Disconnects from the MQTT broker."""
        self._client.disconnect()

    def switch(self, deviceId: str, desired_isOn: bool) -> None:
        """Sends a command to switch a device on or off.

        Publishes a Switch.Set RPC command to the device with the desired state.

        @param deviceId The ID of the target device.

        @param desired_isOn Desired state of the switch (True for ON, False
        for OFF).
        """
        # used for debugging only
        if not USE_MQTT:
            self._on_update_callback(deviceId, "isOn", desired_isOn)
            return

        payload = {
            "id": 1,
            "src": "user",
            "method": "Switch.Set",
            "params": {"id": 0, "on": desired_isOn},
        }
        # Publish the switch command
        self._client.publish(deviceId + self._sub_topic, json.dumps(payload))
