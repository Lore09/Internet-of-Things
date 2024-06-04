import datetime
import yaml
import requests

class AlarmScheduler():

    def __init__(self):
        super().__init__()
    
    def load_alarms(self, alarms_path = './alarms.yaml'):
        # load alarms from file
        self._alarms_path = alarms_path
        with open(self._alarms_path, 'r') as file:
            alarms = yaml.load(file, Loader=yaml.FullLoader)
            self._alarms = alarms

    def get_alarms(self):
        return self._alarms['devices']
    
    def add_alarm(self, device_id, alarm):
        self._alarms[device_id].append(alarm)
        self.save_alarms()
    
    def remove_alarm(self, device_id, alarm):
        self._alarms[device_id].remove(alarm)
        self.save_alarms()

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
                    if now.weekday() in alarm['days'] and now.time() == alarm_time:
                        self.trigger_alarm(entry['device_id'], alarm)
                        continue