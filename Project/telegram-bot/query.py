import requests
from datetime import datetime
from day_mapping import DayMapping
day_mapping = DayMapping()

def fetch_devices(URL_REQUEST):
    """
    function that do the http request and returns 
    - a formatted text that could be sent by the bot
    - a list of devices ids
    """

    text = ""
    device_names = []

    try:
        response = requests.get(f"{URL_REQUEST}/api/devices")
        # Raise an error for bad responses (4xx and 5xx)
        response.raise_for_status()
        # Parse the JSON response
        data = response.json()

        print(data)
        devices = data["devices"]

        for device in devices:
            name = device["name"]
            device_names.append(name)

        text = "The devices are \n"
        for name in device_names:
            text += f"{name}\n"

    except requests.exceptions.RequestException as e:
        text = f"An error occurred while fetching data {e}"

    return text, device_names


def fetch_alarms(URL_REQUEST):
    """
    function that do the http request and returns
    - a formatted text that could be sent by the bot
    - the json data  
    """

    text = ""
    data = None

    try:
        response = requests.get(f"{URL_REQUEST}/api/alarms")
        # Raise an error for bad responses (4xx and 5xx)
        response.raise_for_status()
        # Parse the JSON response
        data = response.json()
        
        # Define the desired date format
        date_format = "%A %d %B %Y at %H:%M"

        # Initialize the formatted message
        formatted_message = "Data received:\n\n"
        
        # Process each id and its timestamps
        data = data["devices"]

        for item in data:
            formatted_message += f"ID: {item['device_id']}\n"
            formatted_message += "Timestamps:\n"
            
            num_alarm = 1

            for alarm in item["alarms"]:
                days = alarm.get("days", None)

                if days is None:
                    # process the alarm without periodicity

                    # Extract date and time
                    date_str = alarm["date"]
                    time_str = alarm["time"]

                    # Combine date and time into a single string
                    datetime_str = date_str + " " + time_str

                    # Parse the combined string into a datetime object
                    datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")

                    # Format the datetime object to a readable string
                    formatted_timestamp = datetime_obj.strftime(date_format)
                    formatted_message += f"  {num_alarm}. {formatted_timestamp}\n"
                else:
                    # process the alarm with periodicity

                    formatted_message += f"  {num_alarm}. "
                    for day in days:
                        # add the periodic days
                        formatted_message += f"{day_mapping.get_day_from_num(day)} "
                    
                    # add the time
                    formatted_message += f"at {alarm['time']}\n"

                num_alarm += 1
                    

            formatted_message += "\n"
        
        text = formatted_message

    except requests.exceptions.RequestException as e:
        text = f"An error occurred while fetching data {e}"

    return text, data



def query_remove(URL_REQUEST, device_id, alarm_id):
    data = {"device_id": device_id, "time": alarm_id}
    response = requests.post(f"{URL_REQUEST}/api/remove_alarm", data=data)
    return response.status_code


def query_add(URL_REQUEST, device_id, type_add, date, time):
    if type_add == "date":
        data = {"device": device_id, "type": type_add, "date": date, "time": time}
    elif type_add == "periodic":
        data = {"device": device_id, "type": type_add, "days": date, "time": time}
    else:
        print("Error: type_add is wrong")
    
    response = requests.post(f"{URL_REQUEST}/api/add_alarm", json=data)
    return response.status_code


def query_trigger(URL_REQUEST, device_id):
    data = {"device_id": device_id}
    response = requests.post(f"{URL_REQUEST}/api/trigger_alarm", data=data)
    return response.status_code


def query_stop(URL_REQUEST, device_id):
    data = {"device_id": device_id}
    response = requests.post(f"{URL_REQUEST}/api/stop_alarm", data=data)
    return response.status_code
