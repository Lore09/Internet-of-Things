from datetime import datetime
import pandas as pd
from analyze.read_from_db import read_data_with_time_period
from analyze.analyze_sleep import detect_sleep_periods


def get_resleep_minutes(InfluxDB, names, pillow_weight, head_weight, how_many_minutes=5):

    start_time = f"-{how_many_minutes}m"

    # read data
    df_pressure_data = read_data_with_time_period(InfluxDB, names, start_time)

    sleep_duration, sleep_periods = detect_sleep_periods(df_pressure_data, names, pillow_weight, head_weight, \
                                                                min_sleep_duration_minutes=1, time_unit_hour=False)

    return sleep_duration
