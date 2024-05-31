import pandas as pd
from influxdb_client import InfluxDBClient


def compute_first_derivative(df, columnName):
    # Sort the DataFrame by time to ensure correct order
    df.sort_values(by='time', inplace=True)
    # Compute the difference between consecutive rows
    df[f'{columnName}_diff'] = df[columnName].diff()
    # return df_diff
    
    # diff_df = df[columnName].diff()
    print(df.tail(20), "\n")
    print(df.head(10))


def more_robust_fist_derivative(df, columnName):
    """
    before computing the diff, we compute a mean of three datapoints
    in order to have more robust values. 
    The new value at time t will the mean between the values at time t-1, t, t+1 
    """
    
    # Compute the mean of values at times t-1, t, and t+1
    df[f'{columnName}_mean'] = df[columnName].rolling(window=3, center=True).mean()
    # Compute the difference between consecutive rows
    df[f'{columnName}_diff'] = df[f'{columnName}_mean'].diff()

    print(df.tail(20), "\n")
    print(df.head(10))


url = "http://localhost:1235"
org = "internet-of-things"

bucket = '"pressure-sensor-data"'
token = "mbeY0bBVOmDe4elawgLHEnhWCXrqIq-G6vCFXH45Fn9chls8lVROmDoIfD4g3tJBWsWtqsccQzPTPGI9L3Ddgw=="

_measurement = '"pressure_sensor"'
_field = '"sensor_data"'

query = f'from(bucket: {bucket})\
|> range(start: -12h)\
|> filter(fn: (r) => r._measurement == {_measurement})\
|> filter(fn: (r) => r._field == {_field})'
# |> filter(fn: (r) => r.location == "coyote_creek")'

# query = f'from(bucket: "pressure-sensor-data")\
# |> range(start: -1d)\
# |> filter(fn: (r) => r._measurement == "pressure_sensor")\
# |> filter(fn: (r) => r._field == "sensor_data")'

#establish a connection
client = InfluxDBClient(url=url, token=token, org=org)

#instantiate the QueryAPI
query_api = client.query_api()

#return the table and print the result
result = query_api.query(org=org, query=query)

# results = []
# for table in result:
#     for record in table.records:
#         results.append((record.get_value(), record.get_field(), record.get_time()))
# print(results)

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
#print(df.tail())





compute_first_derivative(df, 'value')
print("\n\n")
more_robust_fist_derivative(df, 'value')