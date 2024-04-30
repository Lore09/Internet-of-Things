import requests
import asyncio
from aiocoap import *
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS



coap_url = 'coap://130.136.2.70:5683'
temp_url = 'http://130.136.2.70:8080/property/temp'
humidity_url = 'http://130.136.2.70:8080/property/hum'

async def update_values(protocol, request):
    temp = requests.get(temp_url).json()['temp']
    humidity = requests.get(humidity_url).json()['hum']

    try:
        response = await protocol.request(request).response
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)

    return temp, humidity, float(str(response.payload)[2:-1])

async def main():
    protocol = await Context.create_client_context()
    request = Message(code=GET, uri=f'{coap_url}')

    temp, humidity, gas = await update_values(protocol=protocol, request=request)
    print(f'Temperature: {temp}\t Humidity: {humidity}\t Gas: {gas}')

    write_and_read_on_db(temp, humidity, gas)


def write_and_read_on_db(tempValue, humValue, gasValue):
    org = "iotclass"
    bucket = "iotclass"
    token = "0RZWMeMgRCXLBRCuSLZkPItZR2LpJ3SHq82pJ2QAJxBekaH_n0G_XmC_LPCymXvHeOiQjguZJBzoEJKB7639kg=="
    
    #establish a connection
    client = InfluxDBClient(url="http://130.136.2.70:9999", token=token, org=org)

    #instantiate the WriteAPI and QueryAPI
    write_api = client.write_api(write_options=SYNCHRONOUS)
    query_api = client.query_api()

    #create and write the point
    p_temp = Point("tempValue").tag("user", "team_ghiaccioli").field("value", tempValue)
    p_hum = Point("humValue").tag("user", "team_ghiaccioli").field("value", humValue)
    p_gas = Point("gasValue").tag("user", "team_ghiaccioli").field("value", gasValue)

    write_api.write(bucket=bucket,org=org,record=[p_temp, p_hum, p_gas])
    
    print("scritto")

    # read
    # query = f'from(bucket: {bucket})\
    # |> range(start: -10m)\
    # |> filter(fn: (r) => r._measurement == "tempValue")\
    # |> filter(fn: (r) => r._field == "temp_level")\
    # |> filter(fn: (r) => r.location == "team_ghiaccioli")'

    # #return the table and print the result
    # result = client.query_api().query(org=org, query=query)
    # results = []
    # for table in result:
    #     for record in table.records:
    #         results.append((record.get_value(), record.get_field()))
    # print(results)


if __name__ == "__main__":
    asyncio.run(main())