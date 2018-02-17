#!/usr/bin/env python3
from racer import Racer
from lap import Lap
from timer import Timer
from queue import PriorityQueue
import datetime
import os

class Manager:

    LAST_LAPS_SZ = 20
    
    """
    Creates the manager with no racers.
    """
    def __init__(self):
        self.next_racer_id = 0
        self.next_lap_id = 0
        self.racers = {}
        self.racers_id = {}
        self.top_laps = PriorityQueue()
        self.count = 0
        self.total = 0
        self.timer = Timer()
        self.queue = []
        self.last_laps = []

    """
    Adds a racer to the team.
    returns the racer id.
    """
    def add_racer(self, name):
        if name in self.racers_id:
            return self.racers_id[name]
        
        racer = Racer(name, self.new_racer_id())
        self.racers[racer.id] = racer
        self.racers_id[racer.name] = racer.id
        
        return racer.id

    """
    Modifies a racer.
    """
    def rename_racer(self, name, newname):
        if name not in self.racers_id:
            return
        if newname in self.racers_id:
            return

        racer_id = self.racers_id[name]
        racer = self.racers[racer_id]

        racer.name = newname
        self.racers_id[newname] = racer_id
        del self.racers_id[name]

    """
    Deletes a racer from the team.
    returns True iff success.
    """
    def del_racer(self, racer):
        if isinstance(racer, str): # delete by name
            if racer not in self.racers_id:
                return False
            
            racer_id = self.racers_id[racer]
            del self.racers_id[racer]
            del self.racers[racer_id]
            return True

        if isinstance(racer, int): # delete by id
            if racer not in self.racers:
                return False

            racer_name = self.racers[racer].name
            del self.racers[racer]
            del self.racers_id[racer_name]
            return True

        return False

    """
    Adds a lap to the racer.
    returns the lap id.
    """
    def add_lap(self, racer_id, time, begin):
        if racer_id not in self.racers:
            return -1
        
        lap = Lap(time, self.new_lap_id(), begin)
        if not self.racers[racer_id].add_lap(lap):
            return -1

        self.count += 1
        self.total += time
        self.top_laps.put((time, (racer_id, lap.id)))

        if self.top_laps.qsize() > 30:
            pq = PriorityQueue()
            while pq.qsize() < 30:
                pq.put(self.top_laps.get())
            self.top_laps = pq
        
        return lap.id

    """
    Transfers the lap from racer1 to racer2.
    returns True iff success.
    """
    def transfer_lap(self, racer_id1, racer_id2, lap_id):
        if racer_id1 not in self.racers:
            return False

        if racer_id2 not in self.racers:
            return False

        (valid, lap) = self.racers[racer_id1].del_lap(lap_id)
        if not valid:
            return False

        # update last laps
        for i, item in enumerate(self.last_laps):
            (l_id, r_id) = item
            if l_id == lap_id:
                self.last_laps[i] = (l_id, racer_id2)

        # update top laps
        pq = PriorityQueue()
        while not self.top_laps.empty():
            (t, (r_id, l_id)) = self.top_laps.get()
            if l_id == lap_id:
                pq.put((t, (racer_id2, lap_id)))
            else:
                pq.put((t, (r_id, l_id)))
        self.top_laps = pq

        return self.racers[racer_id2].add_lap(lap)

    """
    Edits the lap of the racer.
    returns True iff success.
    """
    def edit_lap(self, racer_id, lap_id, time):
        if racer_id not in self.racers:
            return False

        (valid, diff) = self.racers[racer_id].edit_lap(lap_id, time)
        if not valid:
            return False

        # update top laps
        pq = PriorityQueue()
        while not self.top_laps.empty():
            (t, (r_id, l_id)) = self.top_laps.get()
            if l_id == lap_id:
                pq.put((time, (r_id, l_id)))
            else:
                pq.put((t, (r_id, l_id)))
        self.top_laps = pq

        self.total += diff
        return True

    """
    Deletes the lap of the racer.
    returns True iff success.
    """
    def del_lap(self, racer_id, lap_id):
        if racer_id not in self.racers:
            return False

        (valid, lap) = self.racers[racer_id].del_lap(lap_id)
        if not valid:
            return False

        # update last laps
        index = -1
        for i, item in enumerate(self.last_laps):
            (l_id, r_id) = item
            if l_id == lap_id:
                self.last_laps = self.last_laps[0:i] + self.last_laps[(i+1):Manager.LAST_LAPS_SZ]
                break

        # update top laps
        pq = PriorityQueue()
        while not self.top_laps.empty():
            (t, (r_id, l_id)) = self.top_laps.get()
            if l_id != lap_id:
                pq.put((t, (r_id, l_id)))
        self.top_laps = pq

        self.count -= 1
        self.total -= lap.time
        return True

    """
    Returns the overall mean time.
    """
    def mean_time(self):
        if self.count == 0:
            return 0
        
        return self.total / self.count

    """
    Returns the id of the next new racer.
    """
    def new_racer_id(self):
        self.next_racer_id += 1
        return self.next_racer_id

    """
    Returns the id of the next new lap.
    """
    def new_lap_id(self):
        self.next_lap_id += 1
        return self.next_lap_id

    """
    Adds the racer at the end of the queue.
    """
    def push_racer(self, racer_id):
        if racer_id not in self.racers:
            return False

        self.queue.append(racer_id)
        return True

    """
    Adds the racer at the position po in the queue.
    """
    def insert_racer(self, racer_id, pos):
        if racer_id not in self.racers:
            return False

        self.queue.insert(pos, racer_id)
        return True

    """
    Removes the racer at position pos from the queue.
    Return its id.
    """
    def pop_racer(self, pos=None):
        if pos == None:
            return self.queue.pop()
        
        return self.queue.pop(pos)

    """
    Starts a lap.
    """
    def start_lap(self):
        self.timer.start()

    """
    Ends a lap and updates the status and data.
    """
    def end_lap(self):
        if len(self.queue) == 0:
            return

        begin = self.timer.begin
        time = self.timer.stop()
        racer_id = self.pop_racer(0)
        lap_id = self.add_lap(racer_id, time, begin)

        if len(self.last_laps) == Manager.LAST_LAPS_SZ:
            self.last_laps.pop(0)

        self.last_laps.append((lap_id, racer_id))

    """
    Ends a lap and updates the status and data.
    """
    def stay_lap(self):
        if len(self.queue) == 0:
            return

        begin = self.timer.begin
        time = self.timer.stop()
        racer_id = self.queue[0]
        lap_id = self.add_lap(racer_id, time, begin)

        if len(self.last_laps) == Manager.LAST_LAPS_SZ:
            self.last_laps.pop(0)

        self.last_laps.append((lap_id, racer_id))

    """
    Logs the current state.
    """
    def print_log(self):
        path = "logs/" + datetime.datetime.fromtimestamp(self.timer.current()).strftime('%d_%m_%Y@%H_%M_%S')
        
        s = str(len(self.racers)) + "\n"
        for racer in self.racers.values():
            s += racer.get_log()

        if not os.path.exists("logs"):
            os.makedirs("logs")

        file = open(path,"w")
        file.write(s)
        file.close()

    def load_log(self, path):
        try:
            file = open(path,"r")

            n_racers = int(file.readline()[:-1])

            for i in range(0,n_racers):
                name = file.readline()[:-1]
                racer_id = self.add_racer(name)

                n_laps = int(file.readline()[:-1])
                for i in range(0,n_laps):
                    line = file.readline()[:-1]
                    line = line.split()

                    begin = float(line[0])
                    time = float(line[1])

                    self.add_lap(racer_id, time, begin)
            
            file.close()
        except:
            print("Error: Failed to load data correctly.")
