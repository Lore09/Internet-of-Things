import datetime
import yaml
import requests
import os

class AlarmScheduler():

    def __init__(self):
        super().__init__()
    
    def load_alarms(self, alarms_path):
        # load alarms from file
        self._alarms_path = alarms_path

        # create if not present
        if not os.path.exists(self._alarms_path):
            with open(self._alarms_path, 'w') as file:
                yaml.dump({'devices': []}, file)

        with open(self._alarms_path, 'r') as file:
            alarms = yaml.load(file, Loader=yaml.FullLoader)
            self._alarms = alarms

    def get_alarms(self):
        self.load_alarms(self._alarms_path)
        return self._alarms['devices']
    
    def add_alarm(self, device_id, alarm):

        for entry in self._alarms['devices']:
            if entry['device_id'] == device_id:
                entry['alarms'].append(alarm)
                self.save_alarms()
                return
            
        self._alarms['devices'].append({'device_id': device_id, 'alarms': [alarm]})
        self.save_alarms()
    
    def remove_alarm(self, device_id, time, date, days):

        print(f'Removing alarm for device {device_id} at {time} {date} {days}')
        
        for device in self._alarms['devices']:

            if device['device_id'] == device_id:
                for entry in device['alarms']:

                    if entry["time"] == time:

                        if 'date' in entry and entry['date'] == date:
                            device['alarms'].remove(entry)
                            self.save_alarms()
                            return

                        if 'days' in entry and entry['days'] == days:
                            device['alarms'].remove(entry)
                            self.save_alarms()
                            return

    def save_alarms(self):
        with open(self._alarms_path, 'w') as file:
            yaml.dump(self._alarms, file)

    def trigger_alarm(self, device_id, alarm):
        print(f'Alarm triggered for device {device_id}: {alarm}')

        requests.post("http://127.0.0.1:5000/api/trigger_alarm", data={device_id: alarm})


    def check_alarms(self):
        
        now = datetime.datetime.now().replace(second=0, microsecond=0)

        for entry in self._alarms['devices']:
            for alarm in entry['alarms']:
                
                alarm_time = datetime.datetime.strptime(alarm['time'], '%H:%M').time()

                print( f'Checking alarm for device {entry["device_id"]}: {alarm_time}')

                if 'date' in alarm:
                    alarm_date = datetime.datetime.strptime(alarm['date'], '%Y-%m-%d').date()
                    if now.date() == alarm_date and now.time() == alarm_time:
                        self.trigger_alarm(entry['device_id'], alarm['time'])
                        continue

                if 'days' in alarm:
                    if str(now.weekday()+1) in alarm['days'] and now.time() == alarm_time:
                        self.trigger_alarm(entry['device_id'], alarm)
                        continue