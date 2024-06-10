from datetime import datetime
from query import query_remove

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
    
    if len(splitted_msg) != 3:
        # check message length
        text = "Error: the message doesn't contain the correct information\n" + help_msgs["add_alarm"]
    
    else:
        datetime_msg = splitted_msg[2].split("-")
        
        if len(datetime_msg) != 5:
            # check message length
            text="Error: the message doesn't contain the correct datetime info\n" + help_msgs["add_alarm"]
    
        else:
            try:
                device_id   =     splitted_msg[1]
                day         = int(datetime_msg[0])
                month       = int(datetime_msg[1])
                year        = int(datetime_msg[2])
                hour        = int(datetime_msg[3])
                minute      = int(datetime_msg[4])

                datetime_obj = datetime(year, month, day, hour, minute, 0)

                if datetime_obj <= datetime.now():
                    text = "Error: this moment has already passed"
                else:
                    status_code = query_add(URL_REQUEST, device_id, type_add, datetime_obj)

                    if status_code == 200:
                        text = "Done!"
                    else:
                        text = "Sorry, there is an internal error"

            except ValueError: 
                text = """
                Error: the message doesn't contain the correct information
                The numbers must be integer\n""" + help_msgs["add_alarm"]

    return text
            


def parse_trigger_msg(message, help_msgs, URL_REQUEST):
    text = ""
    splitted_msg = message.split(" ")

    if len(splitted_msg != 2):
        # check message length
        text = "Error: the message doesn't contain the correct info\n" + help_msgs["trigger_alarm"]
    
    else:
        status_code = query_trigger(URL_REQUEST, device_id)

        if status_code == 200:
            text = "Done!"
        else:
            text = "Sorry, there is an internal error"

    return text


def parse_stop_msg(message, help_msgs, URL_REQUEST):
    text = ""
    splitted_msg = message.split(" ")

    if len(splitted_msg != 2):
        # check message length
        text = "Error: the message doesn't contain the correct info\n" + help_msgs["trigger_alarm"]
    
    else:
        status_code = query_stop(URL_REQUEST, device_id)

        if status_code == 200:
            text = "Done!"
        else:
            text = "Sorry, there is an internal error"

    return text

