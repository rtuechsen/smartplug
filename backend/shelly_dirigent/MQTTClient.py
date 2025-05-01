import json
import paho.mqtt.client as mqtt


class MQTTClient:

    def __init__(self):
        self._broker_ip: str = "localhost"
        self._broker_port: int = 8883
        self._keep_alive_seconds = 60
        self._sub_topic: str = "/rpc"
        self._client = mqtt.Client()

        self._client.tls_set(
            ca_certs="/var/lib/mosquitto/ssl/server.crt",  # Path to your CA certificate
            tls_version=mqtt.ssl.PROTOCOL_TLSv1_2  # Use TLSv1.2
        )

        self._client.tls_insecure_set(True)

        self.connect()
        self._client.loop_start()

    def connect(self):

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected successfully to Broker.")

            else:
                print("Connecting to Broker failed. Code:", rc)

        self._client.on_connect = on_connect
        self._client.connect(
            self._broker_ip, self._broker_port, self._keep_alive_seconds
        )

        # TODO: error handling

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

        # TODO: error handling ??? or not possible ??? Might not be required, further research please.
