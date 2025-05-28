import json
import random
import time
import paho.mqtt.client as mqtt
from .logger import Logger
from .error_handler import BackendError
from .admin_settings import USE_MQTT


class MQTTClient:

    def __init__(self, on_update_callback):

        ## The logger instance (singleton) to log events and errors.
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

        # TODO: remove, used for debugging only
        if not USE_MQTT:
            self.init_devices_randomly()

    # TODO: remove, used for debugging only
    def init_devices_randomly(self):

        random.seed(42)

        deviceIds = [
            "shellyplugsg3-b08184a48764",
            "shellyplugsg3-8cbfea90f128",
            "shellyplugsg3-b08184a4b8e4",
            "shellyplugsg3-b08184a654b8",
        ]

        for deviceId in deviceIds:
            # isAvailable: bool = random.choice([True, True, True, False])
            isOn: bool = random.choice([True, False])

            self._on_update_callback(deviceId, "isAvailable", True)
            self._on_update_callback(deviceId, "isOn", True)

    def _connect(self):

        # TODO: type hints
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                client.subscribe("#")
                self._logger.info("Connected successfully to MQTT broker.")
            else:
                raise BackendError("Failed to connect to MQTT broker.")

        self._client.on_connect = on_connect
        self._client.connect(
            self._broker_ip, self._broker_port, self._keep_alive_seconds
        )

    # TODO: type hints
    def _on_message(self, client, userdata, msg):

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

                # TODO: better name for variable - what is this ???
                result = data.get("result")

                # TODO: what could 'result' be? what are the different cases ???
                if isinstance(result, dict) and "output" in result:

                    # TODO: better name for variable - what is this ???
                    output = result.get("output")

                    self._on_update_callback(deviceId, "isOn", output)

            except json.JSONDecodeError:
                # TODO: in which cases can this happen ??? is this only to
                # catch errors in json.loads()
                # TODO: create propper error
                print(f"[{topic}] Invalid JSON in RPC: {payload}")

    def _request_status(self, device_id: str):
        payload = {
            "id": 1,
            "src": "shelly",
            "method": "Switch.GetStatus",
            "params": {"id": 0},
        }
        self._client.publish(device_id + self._sub_topic, json.dumps(payload))

    def disconnect(self):
        self._client.disconnect()

    def switch(self, deviceId: str, desired_isOn: bool):

        # TODO: remove, used for debugging only
        if not USE_MQTT:
            self._on_update_callback(deviceId, "isOn", desired_isOn)

        payload = {
            "id": 1,
            "src": "user",
            "method": "Switch.Set",
            "params": {"id": 0, "on": desired_isOn},
        }

        self._client.publish(deviceId + self._sub_topic, json.dumps(payload))

        # TODO: error handling ??? or not possible ??? Might not be required,
        # further research please.
