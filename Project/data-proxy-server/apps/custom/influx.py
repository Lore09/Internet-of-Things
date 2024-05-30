class Influx:
    def __init__(self):
        super().__init__()

    def set_influx_client(self, client):
        self.client = client