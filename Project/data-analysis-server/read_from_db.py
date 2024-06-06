import re
from datetime import datetime
import pandas as pd
from influxdb_client import InfluxDBClient

url = "http://localhost:1235"
org = "internet-of-things"

bucket = '"pressure-sensor-data"'
token = "mbeY0bBVOmDe4elawgLHEnhWCXrqIq-G6vCFXH45Fn9chls8lVROmDoIfD4g3tJBWsWtqsccQzPTPGI9L3Ddgw=="

_measurement = '"pressure_sensor"'
_field = '"sensor_data"'

bucket = "pressure-sensor-data"
_measurement = "pressure_sensor"
_field = "sensor_data"



def read_first_last_values():
    query_first = f'''
    from(bucket: "{bucket}")
      |> range(start: -365d)
      |> first()
      |> filter(fn: (r) => r._measurement == "{_measurement}")
      |> filter(fn: (r) => r._field == "{_field}")
    '''

    query_last = f'''
    from(bucket: "{bucket}")
      |> range(start: -365d)
      |> last()
      |> filter(fn: (r) => r._measurement == "{_measurement}")
      |> filter(fn: (r) => r._field == "{_field}")
    '''
    
    #establish a connection
    client = InfluxDBClient(url=url, token=token, org=org)

    #instantiate the QueryAPI
    query_api = client.query_api()

    #return the table and print the result
    result = query_api.query(org=org, query=query_first)

    # Initialize a list to hold the records
    records = []

    for table in result:
        for record in table.records:
            records.append({
                'value': record.get_value(),
                'field': record.get_field(),
                'time': record.get_time()
            })

    # Convert the records list to a pandas DataFrame
    df_first = pd.DataFrame(records)


    #return the table and print the result
    result = query_api.query(org=org, query=query_last)

    # Initialize a list to hold the records
    records = []

    for table in result:
        for record in table.records:
            records.append({
                'value': record.get_value(),
                'field': record.get_field(),
                'time': record.get_time()
            })

    # Convert the records list to a pandas DataFrame
    df_last = pd.DataFrame(records)

    client.close()

    df_concatenated = pd.concat([df_first, df_last], ignore_index=True)
    return df_concatenated



def read_data_with_time_period(start_time: datetime, end_time: datetime = None):

    # Convert datetime to RFC3339 format string
    start = start_time.isoformat(timespec='seconds') + 'Z'
    end = end_time.isoformat(timespec='seconds') + 'Z' if end_time else 'now()'

    query = f'''
    from(bucket: "{bucket}")
      |> range(start: {start}, stop: {end})
      |> filter(fn: (r) => r._measurement == "{_measurement}")
      |> filter(fn: (r) => r._field == "{_field}")
    '''
    
    #establish a connection
    client = InfluxDBClient(url=url, token=token, org=org)

    #instantiate the QueryAPI
    query_api = client.query_api()

    #return the table and print the result
    result = query_api.query(org=org, query=query)

    # Initialize a list to hold the records
    records = []

    for table in result:
        for record in table.records:
            records.append({
                'value': record.get_value(),
                'field': record.get_field(),
                'time': record.get_time()
            })

    # Convert the records list to a pandas DataFrame
    df = pd.DataFrame(records)

    client.close()
    return df
    


# start_time = datetime(2024, 6, 1, 0, 0, 0)
# end_time = datetime(2024, 6, 2, 0, 0, 0)

# df = read_data_with_time_period(bucket, _measurement, _field, start_time, end_time)
# print(df.head(10), "\n\n", df.tail(10))
