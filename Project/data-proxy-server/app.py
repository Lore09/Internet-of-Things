from flask import Flask
from src.mqtt import MQTTClient, MQTTConfig

app = Flask(__name__)


broker = 'rebus.ninja'
port = 1883
# Generate a Client ID with the publish prefix.
client_id = 'data-proxy-server'
username = 'test'
password = 'test-user'

registered_devices = []

mqtt_config = MQTTConfig(broker, port, client_id, username, password)
mqtt_client = MQTTClient(mqtt_config, registered_devices)

from src.api import api as api_blueprint
app.register_blueprint(api_blueprint, url_prefix='')

print('Starting MQTT client...')
mqtt_client.run()

if __name__ == '__main__':
    print('App is running...')
    app.run(debug=True)