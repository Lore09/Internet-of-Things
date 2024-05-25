import random
import time
from paho.mqtt import client as mqtt_client

class MQTTConfig:
    def __init__(self, broker_host, broker_port, client_id, username, password):
        self.broker = broker_host
        self.port = broker_port
        self.client_id = client_id
        self.username = username
        self.password = password

class MQTTClient:

    def __init__(self, config):
        self.config = config

    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, self.config.client_id, clean_session=False)
        client.username_pw_set(self.config.username, self.config.password)
        client.on_connect = on_connect
        client.connect_async(self.config.broker, self.config.port, keepalive=60)
        return client

    def publish(self, msg, topic):

        result = self.client.publish(topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")

    def run(self):
        self.client = self.connect_mqtt()
        time.sleep(1)
        self.client.loop_start()