import json
import paho.mqtt.client as mqtt
from .logger import Logger
from .error_handler import BackendError


class MQTTClient:

    def __init__(self, on_update_callback=None):

        ## The logger instance (singleton) to log events and errors.
        self._logger: Logger = Logger()

        self._broker_ip: str = "localhost"
        self._broker_port: int = 8883
        self._keep_alive_seconds = 60
        self._sub_topic: str = "/rpc"
        self._client = mqtt.Client()
        self._username = "mqttuser"
        self._password = "pass"

        # self._client.tls_set(
        #     ca_certs="/var/lib/mosquitto/ssl/server.crt",
        #     certfile="/home/admin/shelly-dirigent/backend/certs/client.crt",
        #     keyfile="/home/admin/shelly-dirigent/backend/certs/client.key",
        # )

        # self._client.tls_insecure_set(True)

        # self._client.username_pw_set(self._username, self._password)

        self.connect()
        self._on_update_callback = on_update_callback
        self._client.on_message = self.on_message
        # TODO: make members protected ???
        self.last_online = {}
        self.last_status = {}
        self._client.loop_start()

    # TODO: make members protected ???
    def connect(self):

        # TODO: userdata -> _
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

    # TODO: make members protected ???
    # TODO: userdata -> _
    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode()

        if topic.endswith("/online"):
            device = topic.split("/")[0]
            state = payload.strip().lower() == "true"

            if self.last_online.get(device) != state:
                self.last_online[device] = state

                # TODO: remove debug print ???
                print(f"[{device}] is {'ONLINE' if state else 'OFFLINE'}")

                if self._on_update_callback:
                    self._on_update_callback(device, "online", state)

        elif topic.endswith("/status/switch:0"):
            device = topic.split("/")[0]
            try:
                data = json.loads(payload)
                output = data.get("output")

                if output is not None:
                    last = self.last_status.get(device)

                    if last != output:
                        self.last_status[device] = output
                        # TODO: remove debug print ???
                        print(
                            f"[{device}] power is: {'ON' if output else 'OFF'}"
                        )

                        if self._on_update_callback:
                            self._on_update_callback(device, "output", output)

            except json.JSONDecodeError as e:
                raise BackendError(
                    f"MQTT client received an invalid JSON for topic "
                    f"{topic}: {payload}"
                ) from e

    def disconnect(self):
        self._client.disconnect()

    def switch(self, deviceId: str, isOn: bool):

        payload = {
            "id": 1,
            "src": "user",
            "method": "Switch.Set",
            "params": {"id": 0, "on": isOn},
        }

        self._client.publish(deviceId + self._sub_topic, json.dumps(payload))

        # TODO: remove debug print
        print(f"Switch command (ON={isOn}) was sent.")

        # TODO: error handling ??? or not possible ??? Might not be required,
        # further research please.
