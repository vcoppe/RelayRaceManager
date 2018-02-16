import time

class Timer:

    def __init__(self):
        self.begin = time.time()

    """
    Starts the timer.
    """
    def start(self):
        self.begin = time.time()

    """
    Returns the elapsed time since the start of the timer.
    """
    def elapsed(self):
        return time.time() - self.begin

    """
    Stops the timer and returns the time elapsed.
    """
    def stop(self):
        self.end = time.time()
        total = self.end - self.begin
        self.begin = self.end
        return total

    """
    Returns the current time.
    """
    def current(self):
        return time.time()
