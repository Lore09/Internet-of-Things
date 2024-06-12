from fastapi import FastAPI
from analyze.analyze_sleep import compute_sleep_time_for_each_day
from analyze.analyze_sleep import compute_sleep_time_for_remaining_days
from analyze.check_resleep import get_resleep_minutes, create_thread_until_woke_up
from app.__init__ import create_influxDB_client, define_names


app = FastAPI()
InfluxDB = create_influxDB_client()
names = define_names()

pillow_weight   = 4  # Example weight of the pillow
head_weight     = 10    # Example weight of the head

# compute the sleep time for each day
# hours_of_sleep_per_day = compute_sleep_time_for_each_day(InfluxDB, names, pillow_weight, head_weight)


@app.get("/")
async def root():
    return {"message": "Hello World"}



@app.get("/analyze/compute_sleep_time_for_each_day")
async def get_sleep_time_for_each_day():
    new_hours_of_sleep_per_day = compute_sleep_time_for_remaining_days(InfluxDB, names, pillow_weight, head_weight)
    return new_hours_of_sleep_per_day


# @app.get("/analyze/check_resleep")
# async def check_resleep():
#     sleep_duration = get_resleep_minutes(InfluxDB, names, pillow_weight, head_weight)
    
#     if sleep_duration >= 1:
#         # trigger again the alarm
#         return {"resleep": 1}
#     else:
#         return {"resleep": 0}

@app.get("/analyze/check_resleep")
async def check_resleep(device_id, alarm):
    """
    function that create a thread that check 
    every 5 minutes if the person woke up
    """
    create_thread_until_woke_up(InfluxDB, names, pillow_weight, head_weight, device_id, alarm)
