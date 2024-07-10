"""
This module contains the Interval class.
"""


class Interval:
    """
    Interval class that represents a range of values.
    """

    def __init__(self, start: float, value):
        self.start = start
        self.end = None
        self.value = value

    def close(self, end: float):
        """
        Close the interval.
        :param end: The end of the interval
        """
        if not self.is_already_closed():
            self.end = end

    def is_already_closed(self):
        """
        Check if the interval is already closed.
        :return: True if the interval is already closed, False otherwise
        """
        return self.end is not None
