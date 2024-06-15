import pandas as pd
import time
import requests
from analyze.read_from_db import read_data_with_time_period

"""
SENSOR DATA CALIBRATION
Done in order to obtain the value recorded by the pressure sensor when the user is and isn't on the bed.
- the sampling rate is augmented
- the alarm sounds for five seconds to signal the user to lay down on the bed
- the micro-controller sends data to the data proxy server related to the values reported by the pressure sensor when the user is on the bed
- the data analysis server computes the average of these values and save it
- the alarm sounds for five seconds to signal the user to get up from the bed
- the micro-controller sends data to the data proxy server related to the values reported by the pressure sensor when the user is not on the bed
- the data analysis server computes the average of these values and save it
- the sampling rate is reset to the default value
"""

headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}


def compute_weight(InfluxDB, names, device_id):

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
    requests.post(names.data_proxy_url + "/api/sampling_rate", data=("device_id=" + device_id + "&sampling_rate=" + str(new_sampling_rate)), headers=headers)

    head_weight = compute_weight(InfluxDB, names, device_id)

    time.sleep(10)

    pillow_weight = compute_weight(InfluxDB, names, device_id)

    # reset the sampling rate
    new_sampling_rate = 20
    requests.post(names.data_proxy_url + "/api/sampling_rate", data=("device_id=" + device_id + "&sampling_rate=" + str(new_sampling_rate)), headers=headers)

    return pillow_weight, head_weight
