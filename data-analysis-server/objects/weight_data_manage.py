import os
import json

class WeightDataManager:
    def __init__(self, file_path):
        self.file_path = file_path
        if not os.path.exists(file_path):
            # Initialize an empty dictionary if the file doesn't exist
            with open(file_path, 'w') as file:
                json.dump({}, file)
    
    def load_data(self):
        with open(self.file_path, 'r') as file:
            return json.load(file)
    
    def save_data(self, data):
        with open(self.file_path, 'w') as file:
            json.dump(data, file, indent=4)
    
    def get_device_data(self, device_id):
        data = self.load_data()
        return data.get(device_id, None)
    
    def update_device_data(self, device_id, device_data):
        data = self.load_data()
        data[device_id] = device_data
        self.save_data(data)
        
    def change_threshold(self, device_id, new_threshold):
        data = self.load_data()
        data[device_id]['threshold_weight'] = new_threshold
        self.save_data(data)
