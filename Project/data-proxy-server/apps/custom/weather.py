import requests

class WeatherChecker:
    def __init__(self):
        super().__init__()

    def init_app(self, api_key, api_url, devices):
        self.api_key = api_key
        self.api_url = api_url
        self.devices = devices
        
    def update_weather(self):
        
        print('Updating weather data')
        for device in self.devices:
            if device['city'] == '':
                continue
            weather_data = self.get_weather(device['city'])
            device['weather'] = weather_data
        
    def get_weather(self, city):
        
        complete_url = self.api_url + "appid=" + self.api_key + "&q=" + city
        
        json_data = requests.get(complete_url).json()
        
        if json_data["cod"] != "404":
                
            return json_data["weather"][0]["main"]