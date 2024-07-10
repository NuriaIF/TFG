"""
This module contains the Chronometer class
"""
import time


class Chronometer:
    """
    This a reusable class that encapsulates the behavior of a chronometer.
    """
    def __init__(self):
        self.start_time = None
        self.stop_time = None
        self.elapsed_seconds = 0
        self.is_running = False

    def start(self) -> None:
        """
        Start the chronometer.
        :return: None
        """
        if not self.is_running:
            self.start_time = time.time()
            self.is_running = True

    def stop(self) -> None:
        """
        Stop the chronometer.
        :return: None
        """
        if self.is_running:
            self.stop_time = time.time()
            self.is_running = False
            self.elapsed_seconds += self.stop_time - self.start_time

    def get_elapsed_time(self) -> float:
        """
        Get the elapsed time of the chronometer.
        (Difference between the start and stop time)
        :return: The elapsed time
        """
        if self.is_running:
            return self.elapsed_seconds + time.time() - self.start_time
        return self.elapsed_seconds

    def reset(self) -> None:
        """
        Resets the state of the chronometer to its initial state.
        :return: None
        """
        self.start_time = None
        self.stop_time = None
        self.elapsed_seconds = 0
        self.is_running = False

    def is_running(self) -> bool:
        """
        Check if the chronometer is running.
        :return: True if the chronometer is running, False otherwise
        """
        return self.is_running

    def is_stopped(self) -> bool:
        """
        Check if the chronometer is stopped.
        :return:
        """
        return not self.is_running

