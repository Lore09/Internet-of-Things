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
    InfluxDB.set_influx_client( url         = INFLUXDB_URL, 
                                token       = INFLUXDB_TOKEN, 
                                org         = INFLUXDB_ORG, 
                                bucket      = INFLUXDB_BUCKET,
                                measurement = INFLUXDB_MEASUREMENT,
                                field       = INFLUXDB_FIELD
                                )
    return InfluxDB


def define_names():

    DF_PRESSURE_VALUE   = os.getenv('DF_PRESSURE_VALUE',    None)
    DF_FIELD            = os.getenv('DF_FIELD',             None)
    DF_TIME             = os.getenv('DF_TIME',              None)
    
    DF_SLEEP_HOURS_DATE = os.getenv('DF_SLEEP_HOURS_DATE',  None)
    DF_SLEEP_HOURS_H    = os.getenv('DF_SLEEP_HOURS_H',     None)

    names = Names()
    names.define(DF_PRESSURE_VALUE, DF_FIELD, DF_TIME, DF_SLEEP_HOURS_DATE, DF_SLEEP_HOURS_H)

    return names
