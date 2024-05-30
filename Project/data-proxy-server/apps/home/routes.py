# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from apps import registered_devices, mqtt_client, influx
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
    data = list(request.form.keys())

    mqtt_client.publish('trigger_alarm', f'devices/{data[0]}')

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

            print(request.form.to_dict())
            write_api.write(influx.bucket, 
                            influx.org, 
                            record=request.form.to_dict())

        return make_response('OK', 200)
    except Exception as e:
        print(e)
        return make_response(f'Error: {e}', 500)