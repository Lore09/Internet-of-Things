# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module
from apps.custom.mqtt import MQTTClient, MQTTConfig

from flask_cdn import CDN

db = SQLAlchemy()
login_manager = LoginManager()
cdn = CDN()

mqtt_client = MQTTClient()
registered_devices = []

def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)

def register_blueprints(app):
    for module_name in ('authentication', 'home'):
        module = import_module('apps.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)

def configure_database(app):

    @app.before_first_request
    def initialize_database():
        try:
            db.create_all()
        except Exception as e:

            print('> Error: DBMS Exception: ' + str(e) )

            # fallback to SQLite
            basedir = os.path.abspath(os.path.dirname(__file__))
            app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')

            print('> Fallback to SQLite ')
            db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()

def configure_mqtt(app):

    # get the MQTT configuration
    broker = app.config.get('MQTT_BROKER_ADDRESS')
    port = int(app.config.get('MQTT_BROKER_PORT'))
    username = app.config.get('MQTT_USERNAME')
    password = app.config.get('MQTT_PASSWORD')

    client_id = app.config.get('CLIENT_ID')

    mqtt_config = MQTTConfig(broker, port, client_id, username, password)

    # print the configuration
    print('> MQTT Broker: ' + broker)
    print('> MQTT Port  : ' + str(port))
    print('> MQTT User  : ' + username)
    print('> MQTT Pass  : ' + password)
    print('> MQTT Client: ' + client_id)

    # Create mqtt client
    mqtt_client.init_client(app, mqtt_config, registered_devices)

    # Start the client
    mqtt_client.run()


def create_app(config):

    # Read debug flag
    DEBUG = (os.getenv('DEBUG', 'False') == 'True')

    # Contextual
    static_prefix = '/static' if DEBUG else '/'

    app = Flask(__name__,static_url_path=static_prefix)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    configure_mqtt(app)

    if not DEBUG and 'CDN_DOMAIN' in app.config:
        cdn.init_app(app)

    return app
