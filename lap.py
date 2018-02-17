#!/usr/bin/env python3
class Lap:

    """
    Creates a new lap.
    """
    def __init__(self, time, lap_id, begin):
        self.time = time
        self.id = lap_id
        self.begin = begin

    """
    Changes the time of this lap.
    """
    def edit(self, time):
        self.time = time

    """
    String representation of the info of the lap.
    """
    def get_log(self):
        return str(self.begin) + " " + str(self.time) + "\n"
