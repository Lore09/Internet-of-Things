from datetime import datetime

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from analyze.read_from_db import fetch_devices
from objects.weight_data_manage import WeightDataManager

from analyze.analyze_sleep import compute_sleep_time_for_each_day
from analyze.analyze_sleep import compute_sleep_time_for_remaining_days
from analyze.check_resleep import get_resleep_minutes, create_thread_until_woke_up
from analyze.check_resleep import check_bed_presence
from analyze.setup_device import setup_device
from analyze.data_forecasting import forecast_data
from app.__init__ import create_influxDB_client, define_names


app = FastAPI()
InfluxDB = create_influxDB_client()
names = define_names()
weight_data_manager = WeightDataManager("data/weights.json")

# pillow_weight   = 4  # Example weight of the pillow
# head_weight     = 10    # Example weight of the head

# compute the sleep time for each day
device_names = fetch_devices(names)
print("device_names: ", device_names)
for device in device_names:
    data = weight_data_manager.get_device_data(device)
    if data is None:
        # do the setup process
        print(f"Setup of device {device}")
        pillow_weight, head_weight = setup_device(InfluxDB, names, device)
        threshold_weight = (pillow_weight + head_weight) / 2
        device_data = {"pillow_weight": pillow_weight, "head_weight": head_weight, "threshold_weight": threshold_weight}
        weight_data_manager.update_device_data(device, device_data)
    else:
        pillow_weight   = data['pillow_weight']
        head_weight     = data['head_weight']

    print(f"Computing hour of sleep from {device}")
    # hours_of_sleep_per_day = compute_sleep_time_for_each_day(InfluxDB, names, device, pillow_weight, head_weight)
    hours_of_sleep_per_day = compute_sleep_time_for_remaining_days(InfluxDB, names, device, pillow_weight, head_weight)


@app.get("/")
async def root():
    return {"message": "Hello World"}



@app.get("/analyze/compute_sleep_time_for_each_day")
async def get_sleep_time_for_each_day(device_id):
    data = weight_data_manager.get_device_data(device)
    pillow_weight   = data['pillow_weight']
    head_weight     = data['head_weight']
    new_hours_of_sleep_per_day = compute_sleep_time_for_remaining_days(InfluxDB, names, device_id, pillow_weight, head_weight)
    return new_hours_of_sleep_per_day


@app.get("/analyze/check_sleep")
async def check_resleep(device_id):
    """
    function that create a thread that check 
    every 5 minutes if the person woke up
    """
    data = weight_data_manager.get_device_data(device)
    pillow_weight   = data['pillow_weight']
    head_weight     = data['head_weight']
    create_thread_until_woke_up(InfluxDB, names, device_id, pillow_weight, head_weight, device_id)

    return {"message": "Checking if the person woke up every 5 minutes"}


@app.get("/analyze/sleeping")
async def get_bed_presence(device_id):
    data = weight_data_manager.get_device_data(device)
    pillow_weight   = data['pillow_weight']
    head_weight     = data['head_weight']
    sleeping = check_bed_presence(InfluxDB, names, device_id, pillow_weight, head_weight, device_id)
    return JSONResponse(content={"sleeping": sleeping})


@app.get("/analyze/calibration")
async def get_weights(device_id):
    pillow_weight, head_weight = setup_device(device_id)
    threshold_weight = (pillow_weight + head_weight) / 2
    device_data = {"pillow_weight": pillow_weight, "head_weight": head_weight, "threshold_weight": threshold_weight}
    weight_data_manager.update_device_data(device_id, device_data)
    return device_data


@app.get("/analyze/get_weights")
async def get_weights(device_id):
    data = weight_data_manager.get_device_data(device)
    return data


@app.get("/analyze/set_threshold")
async def get_weights(device_id, new_threshold):
    """
    Method to change the threshold used to detect the presence of a person.
    The default value is the mean between the pillow and head weight
    """
    try:
        new_threshold = int(new_threshold)
    except:
        return {"message": "the new_threshold must be an integer"}
    weight_data_manager.change_threshold(device_id, new_threshold)
    data = weight_data_manager.get_device_data(device)
    return data


@app.get("/analyze/forecast")
async def forecast(device_id, year, month, day):
    try:
        year = int(year)
        month = int(month)
        day = int(day)
    except:
        return {"message": "year, month and day must be integer"}
    day = datetime(year, month, day, 0, 0, 0)
    forecast_data(InfluxDB, names, device_id, day)
    return {"message": "Done!"}
