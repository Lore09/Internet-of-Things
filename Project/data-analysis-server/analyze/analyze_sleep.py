from analyze.read_from_db import read_first_value, read_last_value
from analyze.read_from_db import read_data_with_time_period
from datetime import datetime
import pandas as pd


def from_df_to_dict(names, df):
    """
    function that from a dataframe containing two columns
    - date
    - hours of sleep
    return a dictionary having as key the date
    """

    # Ensure the DataFrame has the required columns
    if not all(column in df.columns for column in [names.df_sleep_hours_date, names.df_sleep_hours_h]):
        raise ValueError("DataFrame must contain 'date' and 'hours' columns")

    # convert the accuracy into integer such that it is JSON compliant
    df[names.df_sleep_hours_accuracy] = df[names.df_sleep_hours_accuracy].astype(int)

    # Convert the DataFrame to a dictionary
    result_dict = df.set_index(names.df_sleep_hours_date)[[names.df_sleep_hours_h, names.df_sleep_hours_accuracy]].to_dict()

    return result_dict



def detect_sleep_periods(pressure_data, names, pillow_weight, head_weight, threshold_factor=0.5, min_sleep_duration_minutes=10, time_unit='h'):
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
    total_sleep_duration = sum((end - start).total_seconds() for start, end in sleep_periods)


    if time_unit == 'h':
        # in hours
        total_sleep_duration = total_sleep_duration / 3600
    elif time_unit == 'm':
        # in minutes
        total_sleep_duration = total_sleep_duration / 60
    elif time_unit == 's':
        # in seconds
        pass
    
    return total_sleep_duration, sleep_periods



def compute_accuracy_in_detecting_presence(sleep_periods):
    
    if len(sleep_periods) > 0:
        # extract the start of the first sleep period
        start_sleep = sleep_periods[0][0]
        
        # detect the last sleeping period before 12 a.m.
        last_sleeping_period_idx = 0

        # print("sleep_periods: ", len(sleep_periods))
        for i in range(len(sleep_periods)):
            if sleep_periods[i][1].hour < 12:
                last_sleeping_period_idx = i

        end_sleep = sleep_periods[last_sleeping_period_idx][1]

        # compute the real sleep duration
        real_sleep_duration = (end_sleep - start_sleep).total_seconds()
        # compute the recorded sleep duration
        recorded_sleep_duration = sum((end - start).total_seconds() for start, end in sleep_periods[:last_sleeping_period_idx+1])

        accuracy = recorded_sleep_duration * 100 / real_sleep_duration

        return accuracy
    
    else:
        return 0


def compute_sleep_time(InfluxDB, names, client_id, pillow_weight:int, head_weight:int, date, starting_sleep_hour):
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

    df = read_data_with_time_period(InfluxDB, names, client_id, start_time, end_time)

    total_sleep_duration, sleep_periods = detect_sleep_periods(df, names, pillow_weight, head_weight)

    accuracy = compute_accuracy_in_detecting_presence(sleep_periods)

    return end_time, total_sleep_duration, accuracy



def loop_over_dates(InfluxDB, names, client_id, start_date, end_date, pillow_weight:int, head_weight:int, starting_sleep_hour):
    # Create an iterator to iterate over the range of dates
    date_iterator = pd.date_range(start=start_date, end=end_date)

    # result list containing tuples of (day, hours_of_sleep)
    hours_of_sleep_per_day = []

    # Iterate over the dates and print datetime objects for each date
    for date in date_iterator:
    
        starting_time_period, hours_of_sleep, accuracy = compute_sleep_time(InfluxDB, names, client_id, pillow_weight, head_weight, date, starting_sleep_hour)
        
        hours_of_sleep_per_day.append((starting_time_period.date(), hours_of_sleep, accuracy))
    
    return hours_of_sleep_per_day



def compute_sleep_time_for_each_day(InfluxDB, names, client_id, pillow_weight:int, head_weight:int, starting_sleep_hour=20):
    """
    We will compute the hours of sleep of a day considering the sleep time
    between starting_sleep_hour of the previous day and starting_sleep_hour pm of the successive day.
    """

    time_column = names.df_time

    # reading the first value in the database (in the last 365 days)
    df_first = read_first_value(InfluxDB, names, client_id)
    # and the last one
    df_last = read_last_value(InfluxDB, names, client_id)

    print("df_first: ", df_first)
    print("df_last: ", df_last)

    # extract the time
    date_first_row = df_first.loc[0, time_column]
    date_second_row = df_last.loc[0, time_column]

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

    # loop over the days to obtain the sleep time for each day
    hours_of_sleep_per_day = loop_over_dates(InfluxDB, names, client_id, start_date.date(), end_date.date(), pillow_weight, head_weight, starting_sleep_hour)

    # saving the result of the computation to avoid re computing it again
    columns_name = [names.df_sleep_hours_date, names.df_sleep_hours_h, names.df_sleep_hours_accuracy]
    df_hours_of_sleep_per_day = pd.DataFrame(hours_of_sleep_per_day, columns=columns_name)
    df_hours_of_sleep_per_day.to_csv(f"{names.sleep_hours_file_name}_{client_id}.csv")

    print("Computed sleep time for each day")
    return hours_of_sleep_per_day



def compute_sleep_time_for_remaining_days(InfluxDB, names, client_id, pillow_weight:int, head_weight:int, starting_sleep_hour=20):
    
    try:
        # reading the csv file 
        df_hours_of_sleep_per_day = pd.read_csv(f"{names.sleep_hours_file_name}_{client_id}.csv")
    except FileNotFoundError:
        df_hours_of_sleep_per_day = None

    if df_hours_of_sleep_per_day is None:
        compute_sleep_time_for_each_day(InfluxDB, names, client_id, pillow_weight, head_weight, starting_sleep_hour=starting_sleep_hour)
        updated_df = pd.read_csv(f"{names.sleep_hours_file_name}_{client_id}.csv")

    else:
        # retrieving the last day for which the hours of sleep were computed
        last_date_file = df_hours_of_sleep_per_day.iloc[-1][names.df_sleep_hours_date]

        # retrieve the last datapoint in the DB
        df_last = read_last_value(InfluxDB, names)
        # retrieve the time of the last datapoint in the db
        last_time_in_db = df_last.loc[0, names.df_time]

        # create the datetime object
        last_date_file = pd.to_datetime(last_date_file)
        last_time_in_db = pd.to_datetime(last_time_in_db)
        
        # retrieve the hour
        end_hour = last_time_in_db.hour
        # adjust the end date based on the hour
        if end_hour > starting_sleep_hour:
            end_date += pd.Timedelta(days=1)

        # loop over the days to obtain the sleep time for the remaining days
        hours_of_sleep_of_remaining_day = loop_over_dates(InfluxDB, names, client_id, last_date_file.date(), last_time_in_db.date(), pillow_weight, head_weight, starting_sleep_hour)

        # creating the dataframe
        columns_name = [names.df_sleep_hours_date, names.df_sleep_hours_h, df_sleep_hours_accuracy]
        hours_of_sleep_of_remaining_day = pd.DataFrame(hours_of_sleep_of_remaining_day, columns=columns_name)

        old_information_minus_last_day = df_hours_of_sleep_per_day.iloc[:-1]
        updated_df = pd.concat([old_information_minus_last_day, hours_of_sleep_of_remaining_day], ignore_index=True)

        updated_df.to_csv(f"{names.sleep_hours_file_name}_{client_id}.csv")
        print("csv file updated")

    # transform the dataframe to dict
    return from_df_to_dict(names, updated_df)

