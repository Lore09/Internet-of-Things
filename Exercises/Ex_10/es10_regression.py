# script that sends a get request every 10 seconds
import time
import requests
import asyncio
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt
import numpy as np
import random

temp_url = 'http://130.136.2.70:8080/property/temp'
humidity_url = 'http://130.136.2.70:8080/property/hum'

endpoint = 'https://api.thingspeak.com/update'
api_key = '0ISZSNACLLOHRNHO'

# Function to create and return a new plot
def create_plot_window(title, x_data):
    plt.ion()
    fig, ax = plt.subplots()
    fig.suptitle(title)
    ax.set_xlim(0, 33)
    ax.set_ylim(0, 50)
    y_data = np.zeros(30)
    line_data, = ax.plot(np.array(x_data), y_data)
    line_pred, = ax.plot(np.array(x_data), y_data)

    return fig, ax, line_data, line_pred

# Function to update a given plot
def update_plot(fig, ax, line_data, line_pred, y_data, y_pred, x_data):

    y = np.array(y_data)
    x = np.array(x_data)

    x_pred = np.array([x[-1], x[-1] + 1, x[-1] + 2])

    # Update the line data
    line_data.set_data(x, y)
    line_pred.set_data(x_pred, y_pred)
    
    # Update y-axis limits based on the new y_data range
    ax.set_ylim(np.min(y) - 30, np.max(y) + 30)
    ax.set_xlim(min(x), max(x)+3)
    
    # Redraw the plot
    fig.canvas.draw()
    fig.canvas.flush_events()


async def update_values():

    # COMMENTED BECAUSE THE API IS NOT AVAIABLE
    # get the temperature and humidity values
    # temp = requests.get(temp_url).json()['temp']
    # humidity = requests.get(humidity_url).json()['hum']

    temp = random.randint(20, 22) + random.random()
    humidity = random.randint(20, 50) + random.random()

    return temp, humidity


async def main():

    temp_values = []
    hum_values = []
    first = False

    x_data = np.arange(30).tolist()

    fig_hum, ax_hum, line_hum_data, line_hum_pred = create_plot_window('Humidity', x_data)
    fig_temp, ax_temp, line_temp_data, line_temp_pred = create_plot_window('Temperature', x_data)

    while True:

        temp, humidity = await update_values()
        temp_values.append(temp)
        hum_values.append(humidity)

        x_data.append(x_data[-1] + 1)
        x_data.pop(0)

        time.sleep(0.5)
        print(f'Temperature: {temp}\t Humidity: {humidity}')

        # if len(temp_values) > 30: # collect 30 samples
        if len(temp_values) > 30: # collect 30 samples
            # show the plot
            temp_values.pop(0)
            hum_values.pop(0)

            # compute
            model_hum = ARIMA(temp_values, order=(5,1,1))
            model_hum_fit = model_hum.fit()

            model_temp = ARIMA(hum_values, order=(5,1,1))
            model_temp_fit = model_temp.fit()

            forecast_temp = model_temp_fit.forecast(steps=3)
            forecast_hum = model_hum_fit.forecast(steps=3)

            update_plot(fig_hum, ax_hum, line_hum_data, line_hum_pred, hum_values, forecast_hum, x_data)
            update_plot(fig_temp, ax_temp, line_temp_data, line_temp_pred, temp_values, forecast_temp, x_data)

            print(f'Forecasted Temperature: {forecast_temp}\t Forecasted Humidity: {forecast_hum}')

        else:
            print(f'Collecting data... {len(temp_values)}/30')

if __name__ == "__main__":
    asyncio.run(main())