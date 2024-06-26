import re
import requests
from datetime import datetime
import pandas as pd


def fetch_devices(names):
    """
    function that do the http request and returns a list of devices ids
    """
    device_names = []

    try:
        response = requests.get(f"{names.data_proxy_url}/api/devices")
        # Parse the JSON response
        data = response.json()

        devices = data["devices"]

        for device in devices:
            name = device["device_id"]
            device_names.append(name)

    except requests.exceptions.RequestException as e:
        pass

    return device_names


def validate_time_range(time_range: str) -> bool:
    # Regex to validate time range format like "-12h", "-30m", "-2d", etc.
    pattern = re.compile(r"^-?\d+[smhdw]$")
    return bool(pattern.match(time_range))


def read_first_value(InfluxDB, names, client_id):
    query_first = f'''
    from(bucket: "{InfluxDB.bucket}")
      |> range(start: -365d)
      |> first()
      |> filter(fn: (r) => r._measurement == "{InfluxDB.measurement}")
      |> filter(fn: (r) => r._field == "{InfluxDB.field}")
      |> filter(fn: (r) => r.client_id == "{client_id}")
    '''
    
    #establish a connection
    client = InfluxDB.client

    #instantiate the QueryAPI
    query_api = client.query_api()

    #return the table and print the result
    result = query_api.query(org=InfluxDB.org, query=query_first)

    # Initialize a list to hold the records
    records = []

    for table in result:
        for record in table.records:
            records.append({
                names.df_pressure_value:    record.get_value(),
                names.df_field:             record.get_field(),
                names.df_time:              record.get_time()
            })

    # Convert the records list to a pandas DataFrame
    df_first = pd.DataFrame(records)

    return df_first



def read_last_value(InfluxDB, names, client_id):
    query_last = f'''
    from(bucket: "{InfluxDB.bucket}")
      |> range(start: -365d)
      |> last()
      |> filter(fn: (r) => r._measurement == "{InfluxDB.measurement}")
      |> filter(fn: (r) => r._field == "{InfluxDB.field}")
      |> filter(fn: (r) => r.client_id == "{client_id}")
    '''
    
    #establish a connection
    client = InfluxDB.client

    #instantiate the QueryAPI
    query_api = client.query_api()

    #return the table and print the result
    result = query_api.query(org=InfluxDB.org, query=query_last)

    # Initialize a list to hold the records
    records = []

    for table in result:
        for record in table.records:
            records.append({
                names.df_pressure_value:    record.get_value(),
                names.df_field:             record.get_field(),
                names.df_time:              record.get_time()
            })

    # Convert the records list to a pandas DataFrame
    df_last = pd.DataFrame(records)

    return df_last



def generate_query_for_time_period(InfluxDB, client_id, start_time, end_time: datetime = None):
    
    query = None

    if isinstance(start_time, datetime):
    
        # Convert datetime to RFC3339 format string
        start = start_time.isoformat(timespec='seconds') + 'Z'
        end = end_time.isoformat(timespec='seconds') + 'Z' if end_time else 'now()'

        query = f'''
                from(bucket: "{InfluxDB.bucket}")
                |> range(start: {start}, stop: {end})
                |> filter(fn: (r) => r._measurement == "{InfluxDB.measurement}")
                |> filter(fn: (r) => r._field == "{InfluxDB.field}")
                |> filter(fn: (r) => r.client_id == "{client_id}")
                '''

    else:
        if validate_time_range(start_time):
            query = f'''
                    from(bucket: "{InfluxDB.bucket}")
                    |> range(start: {start_time})
                    |> filter(fn: (r) => r._measurement == "{InfluxDB.measurement}")
                    |> filter(fn: (r) => r._field == "{InfluxDB.field}")
                    |> filter(fn: (r) => r.client_id == "{client_id}")
                    '''

    return query
    


def read_data_with_time_period(InfluxDB, names, client_id, start_time, end_time: datetime = None):

    query = generate_query_for_time_period(InfluxDB, client_id, start_time, end_time)

    #establish a connection
    client = InfluxDB.client

    #instantiate the QueryAPI
    query_api = client.query_api()

    #return the table and print the result
    result = query_api.query(org=InfluxDB.org, query=query)

    # Initialize a list to hold the records
    records = []

    for table in result:
        for record in table.records:
            records.append({
                names.df_pressure_value:    record.get_value(),
                names.df_field:             record.get_field(),
                names.df_time:              record.get_time()
            })

    # Convert the records list to a pandas DataFrame
    df = pd.DataFrame(records)

    return df
    
