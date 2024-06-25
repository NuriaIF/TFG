class Interval:
    """
    Interval
    """

    def __init__(self, start: float, value):
        self.start = start
        self.end = None
        self.value = value

    def close(self, end: float):
        if not self.is_already_closed():
            self.end = end

    def is_already_closed(self):
        return self.end is not None
