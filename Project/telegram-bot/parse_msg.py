from datetime import datetime
from query import *
from day_mapping import DayMapping
day_mapping = DayMapping()

def parse_remove_msg(message, help_msgs, URL_REQUEST):
    text = ""
    splitted_msg = message.split(" ")
    
    if len(splitted_msg) != 3:
        # check message length
        text = "Error: the message doesn't contain the correct information\n" + help_msgs["remove_alarm"]
    
    else:
        try:
            device_id   =     splitted_msg[1]
            alarm_id    = int(splitted_msg[2])

            status_code = query_remove(URL_REQUEST, device_id, alarm_id)

            if status_code == 200:
                text = "Done!"
            else:
                text = "Sorry, there is an internal error"

        except ValueError: 
            text = """
            Error: the message doesn't contain the correct information
            The two numbers must be integer\n""" + help_msgs["remove_alarm"]

    return text



def parse_add_msg(message, help_msgs, URL_REQUEST):
    text = ""
    splitted_msg = message.split(" ")
    
    if len(splitted_msg) != 4:
        # check message length
        text = "Error: the message doesn't contain the correct information\n" + help_msgs["add_alarm"]
    
    else:
        device_id   =     splitted_msg[1]
        try:
            type_add = int(splitted_msg[2])

            datetime_msg = splitted_msg[3].split("-")
        
            if type_add == 1:
                if len(datetime_msg) != 5:
                    # check message length
                    text = "Error: the message doesn't contain the correct datetime info\n" + help_msgs["add_alarm"]
            
                else:
                    try:
                        day         = int(datetime_msg[0])
                        month       = int(datetime_msg[1])
                        year        = int(datetime_msg[2])
                        hour        = int(datetime_msg[3])
                        minute      = int(datetime_msg[4])

                        datetime_obj = datetime(year, month, day, hour, minute)

                        if datetime_obj <= datetime.now():
                            text = "Error: this moment has already passed"
                        else:
                            datetime_obj = datetime.strptime(f"{datetime_obj}", "%Y-%m-%d %H:%M:%S")
                            datetime_obj = f"{datetime_obj}".split(" ")
                            status_code = query_add(URL_REQUEST, device_id, 'date', datetime_obj[0], datetime_obj[1][:-3])
                            if status_code == 200:
                                text = "Done!"
                            else:
                                text = f"Sorry, there is an internal error {status_code}"

                    except ValueError as e: 
                        text = f"""
                        Error: the message doesn't contain the correct information
                        The numbers must be integer\n{e}\n""" + help_msgs["add_alarm"]

            elif type_add == 2:
                try:
                    time_hour = int(datetime_msg[-2])
                    time_minute = int(datetime_msg[-1])
                    time = f"{time_hour}:{time_minute}"

                    days = []
                    for i in range(len(datetime_msg)-2):
                        day_num = day_mapping.get_num_from_day(datetime_msg[i])
                        days.append(day_num)

                    status_code = query_add(URL_REQUEST, device_id, 'periodic', days, time)

                    if status_code == 200:
                        text = "Done!"
                    else:
                        text = f"Sorry, there is an internal error {status_code}"


                except ValueError as e: 
                    text = f"""
                    Error: the message doesn't contain the correct information
                    The numbers must be integer\n{e}\n""" + help_msgs["add_alarm"]


            else:
                text = "Error: the type must be 1 or 2\n" + help_msgs["add_alarm"]

        except ValueError: 
            text = """
            Error: the typology of the add must be an integer\n""" + help_msgs["add_alarm"]

    return text
            


def parse_trigger_msg(message, help_msgs, URL_REQUEST):
    text = ""
    splitted_msg = message.split(" ")

    if len(splitted_msg) != 2:
        # check message length
        text = "Error: the message doesn't contain the correct info\n" + help_msgs["trigger_alarm"]
    
    else:
        device_id = splitted_msg[1]
        status_code = query_trigger(URL_REQUEST, device_id)

        if status_code == 200:
            text = "Done!"
        else:
            text = "Sorry, there is an internal error"

    return text


def parse_stop_msg(message, help_msgs, URL_REQUEST):
    text = ""
    splitted_msg = message.split(" ")

    if len(splitted_msg) != 2:
        # check message length
        text = "Error: the message doesn't contain the correct info\n" + help_msgs["trigger_alarm"]
    
    else:
        device_id = splitted_msg[1]
        status_code = query_stop(URL_REQUEST, device_id)

        if status_code == 200:
            text = "Done!"
        else:
            text = "Sorry, there is an internal error"

    return text

