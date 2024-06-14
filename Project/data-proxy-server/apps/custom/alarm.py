import datetime
import yaml
import requests
import os

class AlarmScheduler():

    def __init__(self):
        super().__init__()
    
    def init_alarms(self, alarms_path, registered_devices, analysis_server_url):
        # load alarms from file
        self._alarms_path = alarms_path
        self.registered_devices = registered_devices
        self.analysis_server_url = analysis_server_url

        # create if not present
        if not os.path.exists(self._alarms_path):
            self.save_alarms()

        self.reload_alarms()
            
    def reload_alarms(self):
        
        # clear existing alarms
        self.registered_devices.clear()
        
        with open(self._alarms_path, 'r') as file:
            alarms = yaml.load(file, Loader=yaml.FullLoader)
            self.registered_devices.extend(alarms['devices'])

    def get_alarms(self):
        self.reload_alarms()
        return self.registered_devices
    
    def add_alarm(self, device_id, alarm):

        for entry in self.registered_devices:
            if entry['device_id'] == device_id:
                entry['alarms'].append(alarm)
                self.save_alarms()
                return
    
    def remove_alarm(self, device_id, time, date, days):

        print(f'Removing alarm for device {device_id} at {time} {date} {days}')
        
        for device in self.registered_devices:

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
            yaml.dump({'devices': self.registered_devices}, file)

    def trigger_alarm(self, device_id, alarm):
        
        print(f'Checking if sleepig for device {device_id}...')
        
        data = {
            'device_id': device_id
        }
        
        response = requests.post(self.analysis_server_url + "/analyze/sleeping", data=data)
        
        if response.status_code == 200 and response.json()['sleeping'] == False: 
            print(f'Device {device_id} is not sleeping, not triggering alarm')
            return
        
        print(f'Alarm triggered for device {device_id}: {alarm}')

        requests.post("http://127.0.0.1:5000/api/trigger_alarm", data=data)
        
        requests.get( self.analysis_server_url + "/analyze/check_sleep?device_id=" + device_id )


    def check_alarms(self):
        
        now = datetime.datetime.now().replace(second=0, microsecond=0)

        for entry in self.registered_devices:
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