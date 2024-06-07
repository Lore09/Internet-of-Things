from fastapi import FastAPI
from analyze.analyze_data import compute_sleep_time_for_each_day
from app.__init__ import create_influxDB_client

# PYTHONPATH=$(pwd) $HOME/code/bin/fastapi dev app/main.py

app = FastAPI()
InfluxDB = create_influxDB_client()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/analyze/compute_sleep_time_for_each_day")
async def get_sleep_time_for_each_day():
    compute_sleep_time_for_each_day(pillow_weight, head_weight, pressure_column, time_column)