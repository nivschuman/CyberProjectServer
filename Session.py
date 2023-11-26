import datetime


class Session:
    def __init__(self):
        self.data = dict()
        self.creation_date = datetime.datetime.now()

    def seconds_alive(self):
        now_date = datetime.datetime.now()

        return (now_date - self.creation_date).total_seconds()
