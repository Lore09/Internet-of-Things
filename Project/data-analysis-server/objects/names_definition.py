class Names:
    def __init__(self):
        super().__init__()

    def define(self, df_pressure_value, df_field, df_time, df_sleep_hours_date, df_sleep_hours_h):
        self.df_pressure_value = df_pressure_value
        self.df_field = df_field
        self.df_time = df_time

        self.df_sleep_hours_date = df_sleep_hours_date
        self.df_sleep_hours_h = df_sleep_hours_h
        
        