# script that sends a get request every 10 seconds
import time
import requests

temp_url = 'http://130.136.2.70:8080/property/temp'
humidity_url = 'http://130.136.2.70:8080/property/hum'

endpoint = 'https://api.thingspeak.com/update'
api_key = '0ISZSNACLLOHRNHO'

temp_values = []
hum_values = []

def update_values():
    temp = requests.get(temp_url).json()['temp']
    humidity = requests.get(humidity_url).json()['hum']

    return temp, humidity

start_time = time.time()

while True:

    temp, humidity = update_values()
    print(f'Temperature: {temp}\t Humidity: {humidity}')
    temp_values.append(temp)
    hum_values.append(humidity)
    time.sleep(5)

    if time.time() - start_time > 30:
        start_time = time.time()

        temp_avg = sum(temp_values)/len(temp_values)
        humidity_avg = sum(hum_values)/len(hum_values)
        print(f'Average Temperature: {temp_avg}\t Average Humidity: {humidity_avg}')

        requests.get(f'{endpoint}?api_key={api_key}&field1={temp_avg}&field2={humidity_avg}')
        temp_values = []
        hum_values = []