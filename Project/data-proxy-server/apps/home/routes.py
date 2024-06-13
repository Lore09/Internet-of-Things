# -*- encoding: utf-8 -*-

from apps import registered_devices, mqtt_client, influx, alarm_scheduler, weather_checker
from apps.home import blueprint
from flask import render_template, request, redirect, url_for, make_response
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound

@blueprint.route('/index')
@login_required
def index():
    return render_template('pages/alarms.html', segment='index')

@blueprint.route('/accounts/password-reset/')
def password_reset():
    return render_template('accounts/password_reset.html')

@blueprint.route('/accounts/password-reset-done/')
def password_reset_done():
    return render_template('accounts/password_reset_done.html')

@blueprint.route('/accounts/password-reset-confirm/')
def password_reset_confirm():
    return render_template('accounts/password_reset_confirm.html')

@blueprint.route('/accounts/password-reset-complete/')
def password_reset_complete():
    return render_template('accounts/password_reset_complete.html')

@blueprint.route('/accounts/password-change/')
def password_change():
    return render_template('accounts/password_change.html')

@blueprint.route('/accounts/password-change-done/')
def password_change_done():
    return render_template('accounts/password_change_done.html')

@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500

# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None


@blueprint.route('/devices')
@login_required
def devices():
    return render_template('pages/devices.html', cards=registered_devices)

@blueprint.route('/grafana')
@login_required
def grafana():
    return render_template('pages/grafana.html')

@blueprint.route('/api/devices', methods=['GET'])
def get_devices():
    data = {
        'devices': registered_devices
    }
    
    resp = make_response(data, 200)
    resp.headers['Content-Type'] = 'application/json'
    
    return resp

@blueprint.route('/')
@blueprint.route('/alarms')
@login_required
def alarms():
    return render_template('pages/alarms.html', cards=alarm_scheduler.get_alarms())

@blueprint.route('/alarms/add', methods=['GET'])
@login_required
def add_alarm_page():
    return render_template('pages/new_alarm.html', devices=registered_devices)

@blueprint.route('/api/alarms', methods=['GET'])
def get_alarms():
    
    data = {
        'devices': alarm_scheduler.get_alarms()
    }
    resp = make_response(data, 200)
    resp.headers['Content-Type'] = 'application/json'
    
    return resp

@blueprint.route('/api/add_alarm', methods=['POST'])
def add_alarm():
    data = request.json

    device_id = data['device']
    type = data['type']
    time = data['time']

    if type == 'date':
        date = data['date']
        alarm_scheduler.add_alarm(device_id, {'time': time, 'date': date})
    elif type == 'periodic':
        days = data['days']
        alarm_scheduler.add_alarm(device_id, {'time': time, 'days': days})

    if current_user.is_anonymous:
        return make_response('OK', 200)
    else:
        return redirect(url_for('home_blueprint.alarms'))

@blueprint.route('/api/remove_alarm', methods=['POST'])
def remove_alarm():
    
    data = request.form.to_dict()

    if 'date' in data and data['date'] != '':
        alarm_scheduler.remove_alarm(device_id=data["device_id"], time=data["time"], date=data["date"], days=None)
    else:
        days = data["days"].replace("'","").strip('][').split(', ')
        alarm_scheduler.remove_alarm(device_id=data["device_id"], time=data["time"], days=days, date=None)
    
    if current_user.is_anonymous:
        return make_response('OK', 200)
    else:
        return redirect(url_for('home_blueprint.alarms'))

@blueprint.route('/api/sampling_rate', methods=['POST'])
def update_sampling_rate():
    data = request.form.to_dict()

    device_id = data['device_id']
    sampling_rate = data['sampling_rate']
    
    # update the sampling rate of the device
    for device in registered_devices:
        if device['device_id'] == device_id:
            device['sampling_rate'] = sampling_rate
            break

    # send the new sampling rate to the device
    mqtt_client.publish(f'sampling_rate: {sampling_rate}', f'devices/{device_id}')

    return redirect(url_for('home_blueprint.devices')) 

@blueprint.route('/api/city', methods=['POST'])
def update_city():
    data = request.form.to_dict()

    device_id = data['device_id']
    city = data['city']
    
    # update the sampling rate of the device
    for device in registered_devices:
        if device['device_id'] == device_id:
            device['city'] = city
            break
    
    weather_checker.update_weather()
    
    alarm_scheduler.save_alarms()

    return redirect(url_for('home_blueprint.devices')) 

@blueprint.route('/api/trigger_alarm', methods=['POST'])
def trigger_alarm():
    device_id = request.form.to_dict()['device_id']
    
    device = None
    # get device from registered devices
    for dev in registered_devices:
        if dev['device_id'] == device_id:
            device = dev
            break
    
    if device is None:
        return make_response('Device not found', 404)
    
    if 'weather' in device:
        
        if device['weather'] == 'Clear':
            mqtt_client.publish('trigger_alarm 0', f'devices/{device_id}')
        elif device['weather'] == 'Clouds' or device['weather'] == 'Mist':
            mqtt_client.publish('trigger_alarm 1', f'devices/{device_id}')
        elif device['weather'] == 'Rain' or device['weather'] == 'Drizzle' or device['weather'] == 'Thunderstorm':
            mqtt_client.publish('trigger_alarm 2', f'devices/{device_id}')
    else:
        mqtt_client.publish('trigger_alarm', f'devices/{device_id}')

    if current_user.is_anonymous:
        return make_response('OK', 200)
    else:
        return redirect(url_for('home_blueprint.devices'))

@blueprint.route('/api/stop_alarm', methods=['POST'])
def stop_alarm():
    device = request.form.to_dict()['device_id']
    
    mqtt_client.publish('stop_alarm', f'devices/{device}')

    if current_user.is_anonymous:
        return make_response('OK', 200)
    else:
        return redirect(url_for('home_blueprint.devices'))

@blueprint.route('/api/sensor_data', methods=['POST'])
def get_sensor_data():
    
    try:

        with influx.client.write_api() as write_api:

            print(f'Recived sensor data: {request.form.to_dict()}')

            client_id = request.form.get('client_id')
            sensor_data = request.form.get('data')

            payload = f'pressure_sensor,client_id={client_id} sensor_data={sensor_data}'

            write_api.write(influx.bucket, 
                            influx.org, 
                            record=payload)

        return make_response('OK', 200)
    except Exception as e:
        print(e)
        return make_response(f'Error: {e}', 500)