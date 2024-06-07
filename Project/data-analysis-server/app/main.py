from fastapi import FastAPI
from analyze.analyze_data import compute_sleep_time_for_each_day
from app.__init__ import create_influxDB_client, define_names


app = FastAPI()
InfluxDB = create_influxDB_client()
names = define_names()

pillow_weight   = 4  # Example weight of the pillow
head_weight     = 10    # Example weight of the head
# pressure_column_name = 'value'
# time_column_name     = 'time'

hours_of_sleep_per_day = compute_sleep_time_for_each_day(InfluxDB, names, pillow_weight, head_weight)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/analyze/compute_sleep_time_for_each_day")
async def get_sleep_time_for_each_day():
    

    return dict(hours_of_sleep_per_day)

