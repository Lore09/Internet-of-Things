class DayMapping:
    def __init__(self):
        self.map_num_to_day = {
            "1": "MO",
            "2": "TU",
            "3": "WE",
            "4": "TH",
            "5": "FR",
            "6": "SA",
            "7": "SU",
        }
        self.map_day_to_num = {v: k for k, v in self.map_num_to_day.items()}

    def get_day_from_num(self, num):
        return self.map_num_to_day.get(num, "Invalid number")

    def get_num_from_day(self, day):
        return self.map_day_to_num.get(day, "Invalid day")
