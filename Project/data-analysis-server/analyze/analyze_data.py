from analyze.read_from_db import read_data_with_time_period, read_first_last_values
from datetime import datetime
import pandas as pd


def detect_sleep_periods(pressure_data, names, pillow_weight, head_weight, threshold_factor=0.5, min_sleep_duration_minutes=10):
    """
    Detects the starting and ending points of multiple sleep periods and computes the total number of hours of sleep.
    
    Parameters:
    pressure_data (pd.DataFrame): DataFrame containing the pressure sensor data with a datetime index.
    pillow_weight (int): Weight of the pillow.
    head_weight (int): Weight of the head.
    threshold_factor (float): Factor to adjust the threshold for detecting head on pillow. Default is 0.5, i.e. it is the mean between the two weights.
    min_sleep_duration_minutes (int): Minimum duration of a sleep period to be considered valid, in minutes. Default is 10 minutes.
    
    Returns:
    float: Total number of hours of sleep.
    list: List of tuples with start and end timestamps of each sleep period.
    """

    pressure_column = names.df_pressure_value
    time_column = names.df_time
    
    # Calculate the threshold for detecting head on pillow
    # threshold = pillow_weight + threshold_factor * head_weight
    threshold = (pillow_weight + head_weight) * threshold_factor
    
    # Identify periods when pressure exceeds the threshold
    pressure_data['sleep'] = pressure_data[pressure_column] > threshold
    
    # Find the start and end points of each sleep period
    sleep_periods = []
    is_sleeping = False
    sleep_start = None
    
    for idx, row in pressure_data.iterrows():
        timestamp = row[time_column]
        if row['sleep'] and not is_sleeping:
            sleep_start = timestamp
            is_sleeping = True
        elif not row['sleep'] and is_sleeping:
            sleep_end = timestamp
            sleep_duration = (sleep_end - sleep_start).total_seconds()
            if sleep_duration >= min_sleep_duration_minutes:
                sleep_periods.append((sleep_start, sleep_end))
            is_sleeping = False
    
    # If the last period is still sleeping at the end of the data
    if is_sleeping:
        sleep_end = pressure_data.iloc[-1][time_column]
        sleep_duration = (sleep_end - sleep_start).total_seconds()
        if sleep_duration >= min_sleep_duration_minutes:
            sleep_periods.append((sleep_start, sleep_end))
    
    # Calculate the total sleep duration in hours
    total_sleep_duration = sum((end - start).total_seconds() for start, end in sleep_periods) / 3600
    
    return total_sleep_duration, sleep_periods



def compute_sleep_time(InfluxDB, names, pillow_weight:int, head_weight:int, date, starting_sleep_hour):
    """
    This function will compute the hours of sleep given
    - weight0: the value returned by the sensor with only the pillow
    - weight1: the value returned by the sensor with the head too
    - the date
    - the hour from which the 24 hours must start
    - the name of the dataframe column containing the pressure sensor values
    - the name of the dataframe column containing the time value
    """

    # create the datetime object of the previous day at the correct hour
    start_time = date - pd.Timedelta(days=1)
    start_time = pd.to_datetime(start_time.date()) + pd.Timedelta(hours=starting_sleep_hour)
    
    # create the datetime object of the current day at the correct hour
    end_time = pd.to_datetime(date.date()) + pd.Timedelta(hours=starting_sleep_hour)

    df = read_data_with_time_period(InfluxDB, names, start_time, end_time)

    total_sleep_duration, sleep_periods = detect_sleep_periods(df, names, pillow_weight, head_weight)

    return start_time, total_sleep_duration



def compute_sleep_time_for_each_day(InfluxDB, names, pillow_weight:int, head_weight:int, starting_sleep_hour=20):
    """
    We will compute the hours of sleep of a day considering the sleep time
    between starting_sleep_hour of the previous day and starting_sleep_hour pm of the successive day.
    """

    time_column = names.df_time

    # reading the first value in the database (in the last 365 days)
    # and the last one
    df_first_last = read_first_last_values(InfluxDB, names)

    # extract the time
    date_first_row = df_first_last.loc[0, time_column]
    date_second_row = df_first_last.loc[1, time_column]

    # Create datetime objects
    start_date = pd.to_datetime(date_first_row)
    end_date = pd.to_datetime(date_second_row)

    # Extract the hours from start and end dates
    start_hour = start_date.hour
    end_hour = end_date.hour

    # Adjust the start and end dates based on the hours
    if start_hour > starting_sleep_hour:
        start_date += pd.Timedelta(days=1)
    if end_hour > starting_sleep_hour:
        end_date += pd.Timedelta(days=1)

    # Create an iterator to iterate over the range of dates
    date_iterator = pd.date_range(start=start_date.date(), end=end_date.date())

    # result list containing tuples of (day, hours_of_sleep)
    hours_of_sleep_per_day = []

    # Iterate over the dates and print datetime objects for each date
    for date in date_iterator:
    
        starting_time_period, hours_of_sleep = compute_sleep_time(InfluxDB, names, pillow_weight, head_weight, date, starting_sleep_hour)
        
        hours_of_sleep_per_day.append((starting_time_period.date(), hours_of_sleep))


    # saving the result of the computation to avoid re computing it again
    columns_name = [names.df_sleep_hours_date, names.df_sleep_hours_h]
    df_hours_of_sleep_per_day = pd.DataFrame(hours_of_sleep_per_day, columns=columns_name)
    df_hours_of_sleep_per_day.to_csv("hours_of_sleep_per_day.csv")

    return hours_of_sleep_per_day

