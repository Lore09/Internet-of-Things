# script that sends a get request every 10 seconds
import time
import requests
import asyncio
from aiocoap import *

coap_url = 'coap://130.136.2.70:5683'
temp_url = 'http://130.136.2.70:8080/property/temp'
humidity_url = 'http://130.136.2.70:8080/property/hum'

endpoint = 'https://api.thingspeak.com/update'
api_key = '0ISZSNACLLOHRNHO'

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

    temp_values = []
    hum_values = []

    #coap setup
    protocol = await Context.create_client_context()
    request = Message(code=GET, uri=f'{coap_url}')

    start_time = time.time()    
    while True:

        temp, humidity, gas = await update_values(protocol=protocol, request=request)
        time.sleep(5)
        print(f'Temperature: {temp}\t Humidity: {humidity}\t Gas: {gas}')
        temp_values.append(temp)
        hum_values.append(humidity)

        if time.time() - start_time > 30:
            start_time = time.time()

            temp_avg = sum(temp_values)/len(temp_values)
            humidity_avg = sum(hum_values)/len(hum_values)
            print(f'Average Temperature: {temp_avg}\t Average Humidity: {humidity_avg}')

            requests.get(f'{endpoint}?api_key={api_key}&field1={temp_avg}&field2={humidity_avg}')
            temp_values = []
            hum_values = []

if __name__ == "__main__":

    asyncio.run(main())