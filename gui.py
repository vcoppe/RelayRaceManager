import tkinter as tk
from manager import Manager
import time

title_font = ("Helvetica", 12, 'bold')
timer_font = ("Helvetica", 60, 'bold')
bg_color = 'white'

def convert(t):
    m = t // 60
    t -= m * 60
    s = t // 1
    return "%02d:%02d" % (m, s)

class AddRacer(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.parent = master
        self.name = tk.Label(self, text="Ajouter un coureur", font=title_font)
        self.textfield = tk.Entry(self)

        def callback(event=None):
            racer = self.textfield.get()
            racer = racer.replace(" ", "_")
            if len(racer) == 0:
                return
            self.parent.manager.add_racer(racer)
            self.textfield.delete(0, 'end')
            self.parent.update()
        
        self.validate = tk.Button(self, text="OK", command=callback)
        self.textfield.bind("<Key-Return>", callback)
        
        self.name.grid(row=0, column=0, columnspan=2)
        self.textfield.grid(row=1, column=0)
        self.validate.grid(row=1, column=1)

    def update(self):
        pass

class AllRacers(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.parent = master
        self.list = []
        
        self.name = tk.Label(self, text="Coureurs", font=title_font)
        self.name.grid(row=0, column=0)
        self.name2 = tk.Label(self, text="File", font=title_font)
        self.name2.grid(row=0, column=3)

        def callback():
            if len(self.list) == 0:
                return
            if len(self.listbox.curselection()) == 0:
                return
            index = self.listbox.curselection()[0]
            racer = self.list[index]
            if racer not in self.parent.manager.racers_id:
                return
            self.parent.manager.push_racer(self.parent.manager.racers_id[racer])
            self.parent.update()
            
            self.listbox.selection_set(index)
            self.listbox.activate(index)
            self.listbox.see(index)

        def callback2():
            if len(self.list) == 0:
                return
            if len(self.listbox.curselection()) == 0:
                return
            racer = self.list[self.listbox.curselection()[0]]
            if racer not in self.parent.manager.racers_id:
                return
            viewer = tk.Toplevel(self)
            viewer.title("Stats de %s" % racer)

            scroll = tk.Scrollbar(viewer, orient=tk.VERTICAL)
            scroll.grid(row=0, column=1, sticky=tk.N+tk.S)

            listbox = tk.Listbox(viewer, height=30, width=120, yscrollcommand=scroll.set)
            listbox.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
            scroll['command'] = listbox.yview

            laps = []
            for lap in self.parent.manager.racers[self.parent.manager.racers_id[racer]].laps.values():
                laps.append((lap.time, lap.begin))

            count = 1
            for lap in laps:
                out = ("%003d" % count) + ". " + str(time.strftime("%H:%M", time.localtime(lap[1]))) + " " + convert(lap[0])
                listbox.insert(tk.END, out)
                count += 1

        def callback3():
            if len(self.listbox2.curselection()) == 0:
                return
            racer = self.listbox2.curselection()[0]
            self.parent.manager.pop_racer(racer+1)
            self.parent.update()

            racer = min(racer, len(self.parent.manager.queue)-2)
            
            self.listbox2.selection_set(racer)
            self.listbox2.activate(racer)
            self.listbox2.see(racer)

        self.detail = tk.Button(self, text="Détail", command=callback2)
        self.add = tk.Button(self, text="Ajouter", command=callback)
        self.delete = tk.Button(self, text="Supprimer", command=callback3)

        self.scroll = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.scroll.grid(row=1, column=1, rowspan=3, sticky=tk.N+tk.S)

        self.listbox = tk.Listbox(self, height=20, width=20, yscrollcommand=self.scroll.set)
        self.listbox.grid(row=1, column=0, rowspan=3, sticky=tk.N+tk.S+tk.E+tk.W)
        self.scroll['command'] = self.listbox.yview
        self.detail.grid(row=3, column=2, sticky=tk.N)
        self.delete.grid(row=2, column=2, padx=20)
        self.add.grid(row=1, column=2, sticky=tk.S)

        self.scroll2 = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.scroll2.grid(row=1, column=4, rowspan=3, sticky=tk.N+tk.S)

        self.listbox2 = tk.Listbox(self, height=20, width=20, yscrollcommand=self.scroll2.set)
        self.listbox2.grid(row=1, column=3, rowspan=3, sticky=tk.N+tk.S+tk.E+tk.W)
        self.scroll2['command'] = self.listbox2.yview
        self.listbox2.bind('<KeyPress-Up>', self.up)
        self.listbox2.bind('<KeyPress-Down>', self.down)

    def up(self, event):
        if len(self.listbox2.curselection()) == 0:
            return
        index = self.listbox2.curselection()[0]
        tmp = self.parent.manager.queue[index]
        self.parent.manager.queue[index] = self.parent.manager.queue[index+1]
        self.parent.manager.queue[index+1] = tmp
            
        self.parent.update()
        
        self.listbox2.selection_set(index)
        self.listbox2.activate(index)
        self.listbox2.see(index)

    def down(self, event):
        if len(self.listbox2.curselection()) == 0:
            return
        
        index = self.listbox2.curselection()[0]

        if index+2 >= len(self.parent.manager.queue):
            return
        
        tmp = self.parent.manager.queue[index+2]
        self.parent.manager.queue[index+2] = self.parent.manager.queue[index+1]
        self.parent.manager.queue[index+1] = tmp
            
        self.parent.update()
        
        self.listbox2.selection_set(index)
        self.listbox2.activate(index)
        self.listbox2.see(index)
        
    def update(self):
        index = -1
        index2 = -1
        offset = self.listbox.nearest(0)
        offset2 = self.listbox2.nearest(0)
        if len(self.listbox.curselection()) > 0:
            index = self.listbox.curselection()[0]
        if len(self.listbox2.curselection()) > 0:
            index2 = self.listbox2.curselection()[0]
        
        self.listbox.delete(0, tk.END)
        self.list = sorted(self.parent.manager.racers_id)
        for racer in self.list:
            self.listbox.insert(tk.END, racer)

        self.listbox2.delete(0, tk.END)
        skip = False
        for racer_id in self.parent.manager.queue:
            if not skip:
                skip = True
                continue
            self.listbox2.insert(tk.END, self.parent.manager.racers[racer_id].name)

        if index != -1:
            self.listbox.selection_set(index)
            self.listbox.activate(index)
        if index2 != -1:
            self.listbox2.selection_set(index2)
            self.listbox2.activate(index2)

        self.listbox.yview_scroll(offset, 'units')
        self.listbox2.yview_scroll(offset2, 'units')
        
class LastLaps(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.parent = master
        self.name = tk.Label(self, text="Derniers tours", font=title_font)
        self.list = []

        def callback():
            if len(self.list) == 0:
                return
            if len(self.listbox.curselection()) == 0:
                return
            lap = self.list[self.listbox.curselection()[0]]
            
            viewer = tk.Toplevel(self)
            w = 260
            h = 60

            x = (ws/2) - (w/2)
            y = (hs/2) - (h/2)
            
            viewer.geometry('%dx%d+%d+%d' % (w, h, x, y))
            viewer.title("Modifier un tour")

            tk.Label(viewer, text="Coureur").grid(row=0, column=0, sticky=tk.W)
            tk.Label(viewer, text="Temps").grid(row=1, column=0, sticky=tk.W)
            tk.Label(viewer, text=":").grid(row=1, column=2)

            racer = tk.Entry(viewer)
            racer.insert(tk.END, self.parent.manager.racers[lap[1]].name)
            racer.grid(row=0, column=1, columnspan=3)

            mins = tk.Spinbox(viewer, format="%2.0f", from_=0, to=59, increment=1, width=6)
            secs = tk.Spinbox(viewer, format="%2.0f", from_=0, to=59, increment=1, width=6)

            t = self.parent.manager.racers[lap[1]].laps[lap[0]].time

            mins.insert(tk.END, t // 60)
            secs.insert(tk.END, (t % 60) // 1)

            def mod():
                newname = racer.get()
                m = int(float(mins.get()))
                s = int(float(secs.get()))

                if newname not in self.parent.manager.racers_id:
                    return

                self.parent.manager.edit_lap(lap[1], lap[0], m * 60 + s)

                if lap[1] != self.parent.manager.racers_id[newname]:
                    self.parent.manager.transfer_lap(lap[1], self.parent.manager.racers_id[newname], lap[0])

                viewer.destroy()
                
                self.parent.update()

            tk.Button(viewer, text="OK", command=mod).grid(row=0, column=4, rowspan=2)

            mins.grid(row=1, column=1)
            secs.grid(row=1, column=3)
            
            self.parent.update()

        def callback2():
            if len(self.list) == 0:
                return
            if len(self.listbox.curselection()) == 0:
                return
            lap = self.list[self.listbox.curselection()[0]]
            self.parent.manager.del_lap(lap[1], lap[0])
            self.parent.update()
        
        self.edit = tk.Button(self, text="Modifier", command=callback)       
        self.delete = tk.Button(self, text="Supprimer", command=callback2)

        self.listbox = tk.Listbox(self, height=Manager.LAST_LAPS_SZ, width=20, borderwidth=0, highlightthickness=0)
        self.listbox.grid(row=1, column=0, columnspan=2)
        
        self.name.grid(row=0, column=0, columnspan=2)
        self.edit.grid(row=2, column=0, sticky=tk.W)
        self.delete.grid(row=2, column=1, sticky=tk.E)

    def update(self):
        index = -1
        if len(self.listbox.curselection()) > 0:
            index = self.listbox.curselection()[0]
            
        self.listbox.delete(0, tk.END)
        for (l_id, r_id) in reversed(self.parent.manager.last_laps):
            racer = self.parent.manager.racers[r_id]
            out = "%s %s\n" % (convert(racer.laps[l_id].time), racer.name)
            self.listbox.insert(tk.END, out)

        self.list = list(reversed(self.parent.manager.last_laps))

        if index != -1:
            self.listbox.selection_set(index)
            self.listbox.activate(index)

class Timing(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.parent = master
        
        self.time = tk.Label(self, text=convert(self.parent.manager.timer.elapsed()), font=timer_font)

        def start():
            self.parent.manager.start_lap()
            self.parent.update()

        def stop():
            self.parent.manager.end_lap()
            self.parent.update()

        def stay():
            self.parent.manager.stay_lap()
            self.parent.update()
        
        self.start = tk.Button(self, text="Start", command=start)
        self.startstop = tk.Button(self, text="Stop & Start", command=stop)
        self.stop = tk.Button(self, text="Stop", command=stop)
        self.stay = tk.Button(self, text="Ding ding ding ding ding !", command=stay)
        self.cur = tk.Label(self)
        self.cur.config(text="-", font=("Helvetica", 30))
        
        self.time.grid(row=1, column=0, columnspan=3)
        self.start.grid(row=2, column=0)
        self.startstop.grid(row=2, column=1)
        self.stop.grid(row=2, column=2)
        self.stay.grid(row=3, column=0, columnspan=3)
        self.cur.grid(row=0, column=0, columnspan=3)

    def update(self):
        self.time.config(text=convert(self.parent.manager.timer.elapsed()))
        for racer_id in self.parent.manager.queue:
            self.cur.config(text=">>> "+self.parent.manager.racers[racer_id].name+" <<<")
            break

        if len(self.parent.manager.queue) == 0:
            self.cur.config(text="-")

class MainStats(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.parent = master
        self.name = tk.Label(self, text="Stats", font=title_font)
        self.e1 = tk.Label(self, text="Tours")
        self.e2 = tk.Label(self, text=str(self.parent.manager.count))
        self.e3 = tk.Label(self, text="Moyenne")
        self.e4 = tk.Label(self, text=convert(self.parent.manager.mean_time()))

        def callback():
            viewer = tk.Toplevel(self)
            viewer.title("Troupe des Dragons")

            scroll = tk.Scrollbar(viewer, orient=tk.VERTICAL)
            scroll.grid(row=0, column=1, sticky=tk.N+tk.S)

            listbox = tk.Listbox(viewer, height=30, width=120, yscrollcommand=scroll.set)
            listbox.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
            scroll['command'] = listbox.yview

            laps = []
            for racer in self.parent.manager.racers.values():
                for lap in racer.laps.values():
                    laps.append((lap.begin, lap.time, racer.name))

            laps.sort()
            count = 1
            for lap in laps:
                out = ("%003d" % count) + ". " + str(time.strftime("%H:%M", time.localtime(lap[0]))) + " " + convert(lap[1]) + " " + lap[2]
                listbox.insert(tk.END, out)
                count += 1
        
        self.all = tk.Button(self, text="Voir tous les tours", command=callback)

        self.name.grid(row=0, column=0, columnspan=2)
        self.e1.grid(row=1, column=0, sticky='W', padx=20)
        self.e2.grid(row=1, column=1, sticky='E', padx=20)
        self.e3.grid(row=2, column=0, sticky='W', padx=20)
        self.e4.grid(row=2, column=1, sticky='E', padx=20)
        self.all.grid(row=3, column=0, columnspan=2)

    def update(self):
        self.e2.config(text=str(self.parent.manager.count))
        self.e4.config(text=convert(self.parent.manager.mean_time()))
        
class TopLaps(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.parent = master
        tk.Label(self, text="Meilleurs tours", font=title_font).grid(row=0, column=0)

        self.listbox = tk.Listbox(self, height=10, width=20, borderwidth=0, highlightthickness=0, state='disabled', disabledforeground='black')
        self.listbox.grid(row=1, column=0)

    def update(self):
        self.listbox.config(state='normal')
        self.listbox.delete(0, tk.END)

        tmp = []
        count = 0
        while count < 10 and not self.parent.manager.top_laps.empty():
            item = self.parent.manager.top_laps.get()
            tmp.append(item)
            count += 1

            out = ("%02d" % count) + ". " + convert(item[0]) + " " + self.parent.manager.racers[item[1][0]].name
            self.listbox.insert(tk.END, out)
            
        self.listbox.config(state='disabled')

        for item in tmp:
            self.parent.manager.top_laps.put(item)

class TopRacers(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.parent = master
        tk.Label(self, text="Nombre de tours", font=title_font).grid(row=0, column=0)

        self.listbox = tk.Listbox(self, height=10, width=20, borderwidth=0, highlightthickness=0, state='disabled', disabledforeground='black')
        self.listbox.grid(row=1, column=0)

    def update(self):
        self.listbox.config(state='normal')
        self.listbox.delete(0, tk.END)

        count = 0
        for racer in sorted(self.parent.manager.racers.values(), key=lambda x: (-x.count, x.mean_time())):
            count += 1

            out = ("%02d" % count) + ". " + ("%3d" % racer.count) + " " + racer.name
            self.listbox.insert(tk.END, out)
            
            if count == 10:
                break
            
        self.listbox.config(state='disabled')

class GUI(tk.Frame):
    
    def __init__(self, master):
        super().__init__(master)
        self.config(bg=bg_color)
        top=self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        
        self.manager = Manager()

        self.grid(row=0, column=0)

        self.add_racer = AddRacer(self)
        self.all_racers = AllRacers(self)
        self.last_laps = LastLaps(self)
        self.timing = Timing(self)
        self.main_stats = MainStats(self)
        self.top_laps = TopLaps(self)
        self.top_racers = TopRacers(self)

        # left side
        self.main_stats.grid(row=0, column=0, padx=20, pady=10)
        self.top_laps.grid(row=1, column=0, padx=20, pady=10)
        self.top_racers.grid(row=2, column=0, padx=20, pady=10)

        # center
        self.timing.grid(row=0, column=1, padx=20, pady=10)
        self.all_racers.grid(row=1, column=1, rowspan=2, padx=20, pady=10)

        # right side
        self.add_racer.grid(row=0, column=2, padx=20, pady=20)
        self.last_laps.grid(row=1, column=2, rowspan=2, padx=20, pady=10)

        self.upd()

    def update(self):
        
        self.add_racer.update()
        self.all_racers.update()
        self.last_laps.update()
        self.timing.update()
        self.main_stats.update()
        self.top_laps.update()
        self.top_racers.update()

    def upd(self):

        self.add_racer.update()
        self.all_racers.update()
        self.last_laps.update()
        self.timing.update()
        self.main_stats.update()
        self.top_laps.update()
        self.top_racers.update()

        root.after(500, self.upd)
    
root = tk.Tk()
root.title("Troupe des Dragons")

w = 1060 # width for the Tk root
h = 660 # height for the Tk root

# get screen width and height
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen

# calculate x and y coordinates for the Tk root window
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)

# set the dimensions of the screen 
# and where it is placed
root.geometry('%dx%d+%d+%d' % (w, h, x, y))
root.config(bg = bg_color)
gui = GUI(root)
gui.mainloop()
