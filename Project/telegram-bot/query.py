import requests
from datetime import datetime

def fetch_alarms(URL_REQUEST):
    """
    function that do the http request and returns
    - a formatted text that could be sent by the bot
    - the json data  
    """

    text = ""
    data = None

    try:
        response = requests.get(f"{URL_REQUEST}/api/get_alarms")

        # Raise an error for bad responses (4xx and 5xx)
        response.raise_for_status()

        # Parse the JSON response
        data = response.json()
        
        # Define the desired date format
        date_format = "%A %d %B %Y at %H:%M"

        # Initialize the formatted message
        formatted_message = "Data received:\n\n"
        
        # Process each id and its timestamps
        for item in data:
            formatted_message += f"ID: {item['id']}\n"
            formatted_message += "Timestamps:\n"
            
            for timestamp in item['timestamps']:
                # Convert the timestamp to a datetime object
                dt = datetime.fromisoformat(timestamp.rstrip('Z'))
                # Format the datetime object to a readable string
                formatted_timestamp = dt.strftime(date_format)
                formatted_message += f"  - {formatted_timestamp}\n"

            formatted_message += "\n"
        
        text = formatted_message

    except requests.exceptions.RequestException as e:
        text = f"An error occurred while fetching data"

    return text, data



def query_remove(URL_REQUEST, device_id, alarm_id):
    data = {"device_id": device_id, "time": alarm_id}
    response = requests.post(f"{URL_REQUEST}/api/remove_alarm", data=data)
    return response.status_code
