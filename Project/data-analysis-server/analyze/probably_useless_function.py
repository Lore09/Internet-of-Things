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


def validate_time_range(time_range: str) -> bool:
    # Regex to validate time range format like "-12h", "-30m", "-2d", etc.
    pattern = re.compile(r"^-?\d+[smhdw]$")
    return bool(pattern.match(time_range))


def read_data(bucket, measurement, field, time_range:str):

    # validate the time range
    if not validate_time_range(time_range):
        raise ValueError(f"Invalid time range format: {time_range}")

    query = f'from(bucket: {bucket})\
    |> range(start: {time_range})\
    |> filter(fn: (r) => r._measurement == {measurement})\
    |> filter(fn: (r) => r._field == {field})'
    
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
    return df


# time_range = "-12h"
# df = read_data(bucket, _measurement, _field, time_range)