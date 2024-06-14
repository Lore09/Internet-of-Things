import pandas as pd
import time
import requests
from analyze.read_from_db import read_data_with_time_period

"""
setup of the device, 
to obtain the weight of the pillow and the weight of the head.
To signal the start of the setup process we play the tone,
then for the successive 20 seconds we will record the values of the sensor,
we stop the reproduction of the sound and 
then we will analyze them to obtain the weight of the pillow.
We wait some seconds and then we play the tone again.
We will repeat again the procedure a second time but with the person on the bed 
to obtain the weight of the head.
"""


def compute_weight(InfluxDB, names, device_id):

    headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
    }

    # start the reproduction on the tone
    requests.post(names.data_proxy_url + "/api/trigger_alarm", data=("device_id=" + device_id), headers=headers)
    time.sleep(5)
    # end the reproduction of the tone
    requests.post(names.data_proxy_url + "/api/stop_alarm", data=("device_id=" + device_id), headers=headers)

    # wait to read the values
    how_many_seconds = 20
    time.sleep(how_many_seconds)

    # read the data
    df = read_data_with_time_period(InfluxDB, names, device_id, f"-{how_many_seconds}s")

    # compute weight
    weight = sum(df[names.df_pressure_value])/len(df)
    return weight




def setup_device(InfluxDB, names, device_id):
   
    # increase the sampling rate
    new_sampling_rate = 2
    requests.post(names.data_proxy_url + "/api/sampling_rate", data=("device_id=" + device_id + "&sampling_rate=" + str(new_sampling_rate)))

    head_weight = compute_weight(InfluxDB, names, device_id)

    time.sleep(10)

    pillow_weight = compute_weight(InfluxDB, names, device_id)

    # reset the sampling rate
    new_sampling_rate = 20
    requests.post(names.data_proxy_url + "/api/sampling_rate", data=("device_id=" + device_id + "&sampling_rate=" + str(new_sampling_rate)))

    return pillow_weight, head_weight
