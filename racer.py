#!/usr/bin/env python3
class Racer:

    """
    Creates a new racer with no laps.
    """
    def __init__(self, name, racer_id):
        self.name = name
        self.id = racer_id
        self.laps = {}
        self.count = 0
        self.total = 0

    """
    Adds a lap to this racer.
    lap is a Lap object.
    returns True iff success.
    """
    def add_lap(self, lap):
        if lap.id in self.laps:
            return False
        
        self.laps[lap.id] = lap
        self.count += 1
        self.total += lap.time
        return True

    """
    Changes the time of the lap.
    """
    def edit_lap(self, lap_id, time):
        if lap_id not in self.laps:
            return (False, None)

        diff = time - self.laps[lap_id].time  
        self.total += diff
        self.laps[lap_id].edit(time)
        return (True, diff)

    """
    Deletes a lap to this racer.
    returns True iff success.
    """
    def del_lap(self, lap_id):
        if lap_id not in self.laps:
            return (False, None)
        
        self.count -= 1
        self.total -= self.laps[lap_id].time
        lap = self.laps[lap_id]
        del self.laps[lap_id]
        return (True, lap)

    """
    Returns the mean time over all laps by this racer.
    """
    def mean_time(self):
        if self.count == 0:
            return 0
        
        return self.total / self.count

    """
    Returns the best time over all laps by this racer.
    """
    def best_time(self):
        if self.count == 0:
            return 0
        
        return sorted(self.laps.values(), key=lambda k:k.time)[0].time

    """
    String representation of the info of the racer.
    """
    def get_log(self):
        s = self.name + "\n" + str(self.count) + "\n"
        for lap in self.laps.values():
            s += lap.get_log()
        return s
