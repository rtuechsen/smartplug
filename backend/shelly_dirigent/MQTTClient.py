import json
import paho.mqtt.client as mqtt


class MQTTClient:

    def __init__(self):
        self.broker_ip: str = "localhost"
        self.broker_port: int = 1883
        self.keep_alive_seconds = 60
        self.topic: str = "shellyplugsg3-b08184a654b8/rpc"
        self.client = mqtt.Client()

        self.connect()
        self.client.loop_forever()

    def connect(self):

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected successfully to Broker.")

            else:
                print("Connecting to Broker failed. Code:", rc)

        self.client.on_connect = on_connect
        self.client.connect(self.broker_ip, self.broker_port, self.keep_alive_seconds)

        # TODO: error handling

    def disconnect(self):
        self.client.disconnect()

    def switch(self, isOn: bool):

        payload = {
            "id": 1,
            "src": "user",
            "method": "Switch.Set",
            "params": {"id": 0, "on": isOn},
        }

        self.client.publish(self.topic, json.dumps(payload))
        print(f"Switch command (ON={isOn}) was sent.")

        # TODO: error handling ??? or not possible ???
