# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from apps import registered_devices, mqtt_client, influx, alarm_scheduler
from apps.home import blueprint
from flask import render_template, request, redirect, url_for, make_response
from flask_login import login_required
from jinja2 import TemplateNotFound

@blueprint.route('/index')
@login_required
def index():
    return render_template('pages/index.html', segment='index')

@blueprint.route('/typography')
@login_required
def typography():
    return render_template('pages/typography.html')

@blueprint.route('/color')
@login_required
def color():
    return render_template('pages/color.html')

@blueprint.route('/icon-tabler')
@login_required
def icon_tabler():
    return render_template('pages/icon-tabler.html')

@blueprint.route('/sample-page')
@login_required
def sample_page():
    return render_template('pages/sample-page.html')  

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

@blueprint.route('/alarms')
@login_required
def alarms():
    return render_template('pages/alarms.html', cards=alarm_scheduler.get_alarms())

@blueprint.route('/alarms/add', methods=['GET'])
@login_required
def add_alarm_page():
    return render_template('pages/new_alarm.html', devices=registered_devices)

@blueprint.route('/api/get_alarms', methods=['GET'])
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

    return redirect(url_for('home_blueprint.alarms'))

@blueprint.route('/api/remove_alarm', methods=['POST'])
def remove_alarm():
    
    data = request.form.to_dict()

    if 'date' in data and data['date'] != '':
        alarm_scheduler.remove_alarm(device_id=data["device_id"], time=data["time"], date=data["date"], days=None)
    else:
        days = data["days"].replace("'","").strip('][').split(', ')
        alarm_scheduler.remove_alarm(device_id=data["device_id"], time=data["time"], days=days, date=None)
    
    return redirect(url_for('home_blueprint.alarms'))

@blueprint.route('/form', methods=['POST'])
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

    return redirect(url_for('home_blueprint.devices')) 


@blueprint.route('/api/trigger_alarm', methods=['POST'])
def trigger_alarm():
    device = list(request.form.keys())

    mqtt_client.publish('trigger_alarm', f'devices/{device[0]}')

    return redirect(url_for('home_blueprint.devices'))

@blueprint.route('/api/stop_alarm', methods=['POST'])
def stop_alarm():
    data = list(request.form.keys())
    
    mqtt_client.publish('stop_alarm', f'devices/{data[0]}')

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