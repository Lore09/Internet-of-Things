import time
from paho.mqtt import client as mqtt_client
import random

class MQTTConfig:
    def __init__(self, broker_host, broker_port, client_id, username, password):
        self.broker = broker_host
        self.port = broker_port
        self.client_id = client_id
        self.username = username
        self.password = password

class MQTTClient:

    def __init__(self):
        super().__init__()

    def init_client(self, app, config, registered_devices, alarm_scheduler):
        self.app = app
        self.config = config
        self.registered_devices = registered_devices
        self.alarm_scheduler = alarm_scheduler

    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("> MQTT - Connected to MQTT Broker!")
            else:
                print("> MQTT - Failed to connect, return code %d\n", rc)

        def on_disconnect(client, userdata, rc):
            if rc != 0:
                print("> MQTT - Unexpected disconnection.")

        id = self.config.client_id + ":" + str(random.randint(0, 1000))

        client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, id, clean_session=True)
        client.username_pw_set(self.config.username, self.config.password)
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.connect(self.config.broker, self.config.port, keepalive=60)
        return client

    def publish(self, msg, topic):

        result = self.client.publish(topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")

    def on_message(self, client, userdata, message):
        print(f"Received `{message.payload.decode()}` from `{message.topic}` topic")

        # Check if the message is a device heartbeat
        if message.topic == "devices/heartbeat":
            
            try:
                device = eval(message.payload.decode())
                
            except Exception as e:
                print(f"Error: {e}")
                return
            
            if not any(d['device_id'] == device['name'] for d in self.registered_devices):
                
                device = {
                    'device_id': device['name'],
                    'sampling_rate': device['sampling_rate'],
                    'request_time': [device['request_time']],
                    'average_request_time': 0,
                    'city': '',
                    'weather': '',
                    'alarms': []
                }
                
                self.registered_devices.append(device)
            
            else:
                for d in self.registered_devices:
                    if d['device_id'] == device['name']:
                        
                        d['sampling_rate'] = device['sampling_rate']
                        d['request_time'].append(device['request_time'])
                        
                        # keep only the last 10 request times
                        if len(d['request_time']) >= 10:
                            d['request_time'].pop(0)
                            
                        d['average_request_time'] = round(sum(d['request_time']) / (2 * len(d['request_time'])))
                        break
            
            self.alarm_scheduler.save_alarms()
            

    def run(self):
        self.client = self.connect_mqtt()
        time.sleep(1)

        self.client.on_message = self.on_message
        self.client.subscribe("devices/heartbeat", 0)
        
        self.client.loop_start()