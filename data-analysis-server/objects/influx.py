from influxdb_client import InfluxDBClient

class Influx:
    def __init__(self):
        super().__init__()

    def set_influx_client(self, url, token, org, bucket, measurement, field):
        self.org = org
        self.bucket = bucket
        self.measurement = measurement
        self.field = field
        
        self.client = InfluxDBClient(url=url, token=token, org=org)