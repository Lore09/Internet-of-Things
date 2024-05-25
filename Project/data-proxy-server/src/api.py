from flask import render_template, request, redirect, url_for, Blueprint
from app import registered_devices, mqtt_client

api = Blueprint('api', __name__, template_folder='../templates', static_folder='../static')

@api.route('/')
def dashboard():
    return render_template('dashboard.html', cards=registered_devices)

@api.route('/form', methods=['POST'])
def handle_form():
    data = request.form.to_dict()

    name = list(data.keys())[0]
    sampling_rate = int(data[name])

    # update the sampling rate of the device
    for device in registered_devices:
        if device['name'] == name:
            device['sampling_rate'] = sampling_rate
            break

    # send the new sampling rate to the device
    mqtt_client.publish(f'sampling_rate: {sampling_rate}', f'devices/{name}')

    return redirect(url_for('api.dashboard')) 

@api.route('/api/trigger_alarm', methods=['POST'])
def trigger_alarm():
    data = list(request.form.keys())

    mqtt_client.publish('trigger_alarm', f'devices/{data[0]}')

    return redirect(url_for('api.dashboard'))

@api.route('/api/stop_alarm', methods=['POST'])
def stop_alarm():
    data = list(request.form.keys())
    
    mqtt_client.publish('stop_alarm', f'devices/{data[0]}')

    return redirect(url_for('api.dashboard'))