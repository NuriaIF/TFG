import time


class Chronometer:
    def __init__(self):
        self.start_time = None
        self.stop_time = None
        self.elapsed_seconds = 0
        self.is_running = False

    def start(self):
        if not self.is_running:
            self.start_time = time.time()
            self.is_running = True

    def stop(self):
        if self.is_running:
            self.stop_time = time.time()
            self.is_running = False
            self.elapsed_seconds += self.stop_time - self.start_time

    def get_elapsed_time(self):
        if self.is_running:
            return self.elapsed_seconds + time.time() - self.start_time
        return self.elapsed_seconds

    def reset(self):
        self.start_time = None
        self.stop_time = None
        self.elapsed_seconds = 0
        self.is_running = False

    def is_running(self):
        return self.is_running

    def is_stopped(self):
        return not self.is_running

