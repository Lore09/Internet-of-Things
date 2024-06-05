# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os, random, string

class Config(object):

    basedir = os.path.abspath(os.path.dirname(__file__))

    # Set up the App SECRET_KEY
    SECRET_KEY  = os.getenv('SECRET_KEY', None)
    if not SECRET_KEY:
        SECRET_KEY = ''.join(random.choice( string.ascii_lowercase  ) for i in range( 32 ))

    # CDN Support Settings 
    CDN_DOMAIN  = os.getenv('CDN_DOMAIN' , None)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DB_ENGINE   = os.getenv('DB_ENGINE'   , None)
    DB_USERNAME = os.getenv('DB_USERNAME' , None)
    DB_PASS     = os.getenv('DB_PASS'     , None)
    DB_HOST     = os.getenv('DB_HOST'     , None)
    DB_PORT     = os.getenv('DB_PORT'     , None)
    DB_NAME     = os.getenv('DB_NAME'     , None)

    USE_SQLITE  = True 

    # Mqtt Config
    MQTT_BROKER_ADDRESS = os.getenv('MQTT_BROKER_ADDRESS', 'localhost')
    MQTT_BROKER_PORT    = os.getenv('MQTT_BROKER_PORT', 1883)
    MQTT_USERNAME       = os.getenv('MQTT_USERNAME', '')
    MQTT_PASSWORD       = os.getenv('MQTT_PASSWORD', '')
    CLIENT_ID           = os.getenv('CLIENT_ID', 'data-proxy-server')

    # InfluxDB Config
    INFLUXDB_ADDRESS    = os.getenv('INFLUXDB_ADDRESS', 'localhost')
    INFLUXDB_TOKEN      = os.getenv('INFLUXDB_TOKEN', '')
    INFLUXDB_ORG        = os.getenv('INFLUXDB_ORG', '')
    INFLUXDB_BUCKET     = os.getenv('INFLUXDB_BUCKET', '')

    ALARMS_FILE         = os.getenv('ALARMS_FILE', 'alarms.yaml')
    APP_DATA_PATH       = os.getenv('APP_DATA_PATH', './data/')

    # try to set up a Relational DBMS
    if DB_ENGINE and DB_NAME and DB_USERNAME:

        try:
            
            # Relational DBMS: PSQL, MySql
            SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
                DB_ENGINE,
                DB_USERNAME,
                DB_PASS,
                DB_HOST,
                DB_PORT,
                DB_NAME
            ) 

            USE_SQLITE  = False

        except Exception as e:

            print('> Error: DBMS Exception: ' + str(e) )
            print('> Fallback to SQLite ')    

    if USE_SQLITE:

        # This will create a file in <app> FOLDER
        # TODO - Move this to a more appropriate location
        app_dir = os.path.abspath(APP_DATA_PATH)
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app_dir, 'db.sqlite3')
        print('> USING SQLITE - ' + SQLALCHEMY_DATABASE_URI)
    
class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

class DebugConfig(Config):
    DEBUG = True

# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug'     : DebugConfig
}
