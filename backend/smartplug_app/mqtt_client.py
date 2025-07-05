import json
import random
import paho.mqtt.client as mqtt
from .logger import Logger
from .error_handler import BackendError
from .admin_settings import USE_MQTT


class MQTTClient:
    """
    MQTTClient handles MQTT communication for device status updates and control.
    It listens to topics, parses incoming messages, and sends control messages.
    """

    def __init__(self, on_update_callback) -> None:
        """
        Initialize the MQTT client and set up connection and callbacks.

        :param on_update_callback: Callback function to update device states in the main application.
        """

        self._logger: Logger = Logger()

        self._broker_ip: str = "localhost"
        self._broker_port: int = 1883
        self._keep_alive_seconds: float = 60
        self._sub_topic: str = "/rpc"
        self._client: mqtt.Client = mqtt.Client()

        # TLS --------------------------------------

        # self._username = "mqttuser"
        # self._password = "pass"

        # TODO: generate / add certificates when installing / starting
        # or add them to git and copy them when installing / starting ???

        # self._client.tls_set(
        #     ca_certs="/var/lib/mosquitto/ssl/server.crt",
        #     certfile="/home/admin/shelly-dirigent/backend/certs/client.crt",
        #     keyfile="/home/admin/shelly-dirigent/backend/certs/client.key",
        # )

        # self._client.tls_insecure_set(True)
        # self._client.username_pw_set(self._username, self._password)

        # -------------------------------------------

        self._connect()
        self._on_update_callback = on_update_callback
        self._client.on_message = self._on_message
        self._client.loop_start()

    def _connect(self) -> None:
        """
        Connects to the MQTT broker and subscribes to all topics.
        """

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
        """
        Callback for processing incoming MQTT messages.
        """

        topic = msg.topic
        payload = msg.payload.decode()

        if topic.endswith("/online"):
            deviceId = topic.split("/")[0]
            state = payload.strip().lower() == "true"

            self._on_update_callback(deviceId, "isAvailable", state)
            if state:
                self._request_status(deviceId)

        elif topic.endswith("/status/switch:0"):
            deviceId = topic.split("/")[0]
            try:
                data = json.loads(payload)
                output = data.get("output")

                self._on_update_callback(deviceId, "isOn", output)

            except json.JSONDecodeError as e:
                raise BackendError(
                    f"MQTT client received an invalid JSON for topic "
                    f"{topic}: {payload}"
                ) from e

        elif topic.endswith("/rpc"):
            deviceId = topic.split("/")[0]
            try:
                data = json.loads(payload)
                deviceId = data.get("src")
                rpc_response = data.get("result")

                if isinstance(rpc_response, dict) and "output" in rpc_response:

                    output = rpc_response.get("output")

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
        """
        Requests the current status of a device by sending a Switch.GetStatus RPC.

        :param device_id: The ID of the target device.
        """
        payload = {
            "id": 1,
            "src": "shelly",
            "method": "Switch.GetStatus",
            "params": {"id": 0},
        }
        self._client.publish(device_id + self._sub_topic, json.dumps(payload))

    def disconnect(self) -> None:
        """
        Disconnects from the MQTT broker.
        """
        self._client.disconnect()

    def switch(self, deviceId: str, desired_isOn: bool) -> None:
        """
        Sends a command to switch a device on or off.

        :param device_id: The ID of the target device.
        :param desired_isOn: Desired state of the switch (True for on, False for off).
        """
        # TODO: remove, used for debugging only
        if not USE_MQTT:
            self._on_update_callback(deviceId, "isOn", desired_isOn)
            return

        payload = {
            "id": 1,
            "src": "user",
            "method": "Switch.Set",
            "params": {"id": 0, "on": desired_isOn},
        }

        self._client.publish(deviceId + self._sub_topic, json.dumps(payload))
