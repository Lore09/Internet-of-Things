import os
from objects.influx import Influx
from objects.names_definition import Names
from dotenv import load_dotenv

def create_influxDB_client():

    load_dotenv()

    INFLUXDB_URL              = os.getenv('INFLUXDB_URL',           None)
    INFLUXDB_ORG              = os.getenv('INFLUXDB_ORG',           None)
    INFLUXDB_TOKEN            = os.getenv('INFLUXDB_TOKEN',         None)
    INFLUXDB_BUCKET           = os.getenv('INFLUXDB_BUCKET',        None)
    INFLUXDB_MEASUREMENT      = os.getenv('INFLUXDB_MEASUREMENT',   None)
    INFLUXDB_FIELD            = os.getenv('INFLUXDB_FIELD',         None)

    InfluxDB = Influx()
    InfluxDB.set_influx_client( 
                                url         = INFLUXDB_URL, 
                                token       = INFLUXDB_TOKEN, 
                                org         = INFLUXDB_ORG, 
                                bucket      = INFLUXDB_BUCKET,
                                measurement = INFLUXDB_MEASUREMENT,
                                field       = INFLUXDB_FIELD
                                )
    return InfluxDB


def define_names():

    DF_PRESSURE_VALUE       = os.getenv('DF_PRESSURE_VALUE',        None)
    DF_FIELD                = os.getenv('DF_FIELD',                 None)
    DF_TIME                 = os.getenv('DF_TIME',                  None)
    
    DF_SLEEP_HOURS_DATE     = os.getenv('DF_SLEEP_HOURS_DATE',      None)
    DF_SLEEP_HOURS_H        = os.getenv('DF_SLEEP_HOURS_H',         None)
    DF_SLEEP_HOURS_ACCURACY = os.getenv('DF_SLEEP_HOURS_ACCURACY',  None)
    SLEEP_HOURS_FILE_NAME   = os.getenv('SLEEP_HOURS_FILE_NAME',    None)
    
    DATA_PROXY_URL          = os.getenv('DATA_PROXY_URL',           None)

    names = Names()
    names.define(
                df_pressure_value       = DF_PRESSURE_VALUE, 
                df_field                = DF_FIELD, 
                df_time                 = DF_TIME, 
                df_sleep_hours_date     = DF_SLEEP_HOURS_DATE, 
                df_sleep_hours_h        = DF_SLEEP_HOURS_H, 
                df_sleep_hours_accuracy = DF_SLEEP_HOURS_ACCURACY,
                sleep_hours_file_name   = SLEEP_HOURS_FILE_NAME,
                data_proxy_url          = DATA_PROXY_URL
                )

    return names
