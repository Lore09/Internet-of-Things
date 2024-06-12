import time
from datetime import datetime
import pandas as pd
from analyze.read_from_db import read_data_with_time_period
from analyze.analyze_sleep import detect_sleep_periods

import threading
import requests


def get_resleep_minutes(InfluxDB, names, pillow_weight, head_weight, how_many_minutes=5):

    start_time = f"-{how_many_minutes}m"

    # read data
    df_pressure_data = read_data_with_time_period(InfluxDB, names, start_time)

    sleep_duration, sleep_periods = detect_sleep_periods(df_pressure_data, names, pillow_weight, head_weight, \
                                                                min_sleep_duration_minutes=1, time_unit_hour=False)

    return sleep_duration


def repeat_until_woke_up(InfluxDB, names, pillow_weight, head_weight, device_id, alarm, how_many_minutes=5):
    woke_up = False

    # increase the sampling rate
    new_sampling_rate = 10
    requests.post("http://127.0.0.1:5000/form", data={device_id: new_sampling_rate})
    
    while not woke_up:
        time.sleep(how_many_minutes * 60)
        sleep_duration = get_resleep_minutes(InfluxDB, names, pillow_weight, head_weight, \
                                            how_many_minutes=how_many_minutes)
        if sleep_duration < 1.0:
            """
            if the person sleeps doesn't sleep at least one minute
            in the last 5, then we consider it as woke up
            """
            woke_up = True
        else:
            # otherwise trigger alarm again
            requests.post("http://127.0.0.1:5000/api/trigger_alarm", data={device_id: alarm})
         
    # change the sampling rate to the defualt value
    new_sampling_rate = 30
    requests.post("http://127.0.0.1:5000/form", data={device_id: new_sampling_rate})
    


def create_thread_until_woke_up(InfluxDB, names, pillow_weight, head_weight, device_id, alarm, how_many_minutes=5):
    # Create a thread to run the repeated_execution function with parameters
    execution_thread = threading.Thread(target=repeat_until_woke_up, args=(InfluxDB, names, pillow_weight, \
                                                                            head_weight, device_id, alarm))
    # Start the thread
    execution_thread.start()
