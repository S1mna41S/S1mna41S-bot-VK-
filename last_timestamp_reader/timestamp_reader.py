import json


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class TimeStampReader(metaclass=Singleton):
    def __init__(self):
        self.json_name = "last_timestamp_reader/last_ata.json"
        self.json_item_name = 'last_timestamp'
        self.last_timestamp = self._read_json()

    def _read_json(self):
        with open(self.json_name, 'r') as f:
            data = json.load(f)

        return data[self.json_item_name]

    def get_last_timestamp(self):
        return self.last_timestamp

    def set_new_timestamp(self, new_tstamp):
        print(f'New timestamp: {self.last_timestamp} -> {new_tstamp}')
        self.last_timestamp = new_tstamp
        data = {self.json_item_name: new_tstamp}
        with open(self.json_name, 'w') as f:
            json.dump(data, f)
