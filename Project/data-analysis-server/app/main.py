from fastapi import FastAPI
from fastapi.responses import JSONResponse

from analyze.read_from_db import fetch_devices

from analyze.analyze_sleep import compute_sleep_time_for_each_day
from analyze.analyze_sleep import compute_sleep_time_for_remaining_days
from analyze.check_resleep import get_resleep_minutes, create_thread_until_woke_up
from analyze.check_resleep import check_bed_presence
from app.__init__ import create_influxDB_client, define_names


app = FastAPI()
InfluxDB = create_influxDB_client()
names = define_names()

pillow_weight   = 4  # Example weight of the pillow
head_weight     = 10    # Example weight of the head

# compute the sleep time for each day
device_names = fetch_devices(names)
print("device_names: ", device_names)
for device in device_names:
    hours_of_sleep_per_day = compute_sleep_time_for_each_day(InfluxDB, names, device, pillow_weight, head_weight)


@app.get("/")
async def root():
    return {"message": "Hello World"}



@app.get("/analyze/compute_sleep_time_for_each_day")
async def get_sleep_time_for_each_day(device_id="esp8266-lore"):
    new_hours_of_sleep_per_day = compute_sleep_time_for_remaining_days(InfluxDB, names, device_id, pillow_weight, head_weight)
    return new_hours_of_sleep_per_day


@app.get("/analyze/check_sleep")
async def check_resleep(device_id):
    """
    function that create a thread that check 
    every 5 minutes if the person woke up
    """
    create_thread_until_woke_up(InfluxDB, names, device_id, pillow_weight, head_weight, device_id)

    return {"message": "Checking if the person woke up every 5 minutes"}


@app.post("/analyze/sleeping")
async def get_bed_presence(device_id):
    sleeping = check_bed_presence(InfluxDB, names, device_id, pillow_weight, head_weight, device_id)
    return JSONResponse(content={"sleeping": sleeping})