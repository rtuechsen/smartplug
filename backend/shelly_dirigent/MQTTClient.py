import json
import paho.mqtt.client as mqtt


class MQTTClient:

    def __init__(self, on_update_callback = None):
        self._broker_ip: str = "localhost"
        self._broker_port: int = 1883
        self._keep_alive_seconds = 60
        self._sub_topic: str = "/rpc"
        self._client = mqtt.Client()
        self._username = "mqttuser"
        self._password = "Pass"

        self._client.tls_set(
            ca_certs = "/var/lib/mosquitto/ssl/server.crt",  # Path to your CA certificate
            tls_version = mqtt.ssl.PROTOCOL_TLSv1_2  # Use TLSv1.2
        )

        self._client.tls_insecure_set(True)

        self._client.username_pw_set(self._username, self._password)

        self.connect()
        self._on_update_callback = on_update_callback
        self._client.on_message = self.on_message
        self.last_online = {}
        self.last_status = {}
        self._client.loop_start()

    def connect(self):

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                client.subscribe("#")
                print("Connected successfully to Broker.")

            else:
                print("Connecting to Broker failed. Code:", rc)

        self._client.on_connect = on_connect
        self._client.connect(
            self._broker_ip, self._broker_port, self._keep_alive_seconds
        )
    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode()

        if topic.endswith("/online"):
            device = topic.split("/")[0]
            state = payload.strip().lower() == "true"
            if self.last_online.get(device) != state:
                self.last_online[device] = state
                print(f"[{device}] ist {'ONLINE' if state else 'OFFLINE'}")
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
                        print(f"[{device}] Ausgang: {'EIN' if output else 'AUS'}")
                        if self._on_update_callback:
                            self._on_update_callback(device, "output", output)
            except json.JSONDecodeError:
                print(f"[{topic}] Ungültiges JSON: {payload}")
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
