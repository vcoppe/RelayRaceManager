﻿#!/usr/bin/env python3
import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog
from manager import Manager
import time
import datetime
import os

title_font = ("Helvetica", 12, 'bold')
base_font = ("Helvetica", 12)
button_font = ("Helvetica", 13)
timer_font = ("Helvetica", 60, 'bold')
cur_font = ("Helvetica", 30)
bg_color = "gray80"
frame_bg = None

LOG_INTERVAL = 20 * 60 # seconds

def convert(t):
    m = t // 60
    t -= m * 60
    s = t // 1
    return "%02d:%02d" % (m, s)

def center(toplevel):
    toplevel.update_idletasks()
    sw = toplevel.winfo_screenwidth()
    sh = toplevel.winfo_screenheight()
    ww = toplevel.winfo_width()
    wh = toplevel.winfo_height()
    x = sw//2 - ww//2
    y = sh//2 - wh//2
    toplevel.geometry("{}x{}+{}+{}".format(ww, wh, x, y))
    
class AddRacer(tk.Frame):

    def __init__(self, master):
        super().__init__(master, bg=frame_bg)
        self.parent = master
        self.name = tk.Label(self, text="Ajouter un coureur", font=title_font, bg=frame_bg)
        self.textfield = tk.Entry(self, font=base_font)

        def callback(event=None):
            racer = self.textfield.get()
            racer = racer.replace(" ", "_")
            if len(racer) == 0:
                return
            self.parent.manager.add_racer(racer)
            self.textfield.delete(0, 'end')
            self.parent.update()
        
        self.validate = tk.Button(self, text="OK", command=callback, font=button_font)
        self.textfield.bind("<Key-Return>", callback)
        
        self.name.grid(row=0, column=0, columnspan=2, sticky=tk.S)
        self.textfield.grid(row=1, column=0, padx=(5,0), sticky=tk.N+tk.E)
        self.validate.grid(row=1, column=1, padx=(0,5), sticky=tk.N+tk.W)

        def load_file():
            path = filedialog.askopenfilename(initialdir = "logs",title = "Choisir un fichier")
            self.parent.manager.load_log(path)

        self.load = tk.Button(self, text="Charger depuis un fichier", command=load_file, font=button_font)
        self.load.grid(row=2, column=0, columnspan=2, sticky=tk.S)

        def save_file():
            self.parent.manager.print_log()

        self.save = tk.Button(self, text="Sauver les données", command=save_file, font=button_font)
        self.save.grid(row=3, column=0, columnspan=2, sticky=tk.N)

    def update(self):
        pass

class AllRacers(tk.Frame):

    def __init__(self, master):
        super().__init__(master, bg=frame_bg)
        self.parent = master
        self.list = []
        
        self.name = tk.Label(self, text="Coureurs", font=title_font, bg=frame_bg)
        self.name.grid(row=0, column=0)
        self.name2 = tk.Label(self, text="File", font=title_font, bg=frame_bg)
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
            viewer = tk.Toplevel(self, bg=frame_bg)
            viewer.title("Stats de %s" % racer)

            scroll = tk.Scrollbar(viewer, orient=tk.VERTICAL)
            scroll.grid(row=1, column=1, rowspan=2, sticky=tk.N+tk.S, pady=(0,10))

            legend = tk.Label(viewer, text=" #     Heure  Temps", font=base_font, bg=frame_bg)
            legend.grid(row=0, column=0, sticky=tk.W, padx=(10,0))

            listbox = tk.Listbox(viewer, height=30, width=20, yscrollcommand=scroll.set, borderwidth=0, highlightthickness=0, font=base_font)
            listbox.grid(row=1, column=0, rowspan=2, sticky=tk.N+tk.S+tk.E+tk.W, padx=(10,0), pady=(0,10))
            scroll['command'] = listbox.yview

            avg = tk.Label(viewer, text="Moyenne", font=title_font, bg=frame_bg)
            avg.grid(row=0, column=2, sticky=tk.S, pady=(10,0))


            mean_time = self.parent.manager.racers[self.parent.manager.racers_id[racer]].mean_time()
            dispavg = tk.Label(viewer, text=convert(mean_time), font=base_font, bg=frame_bg)
            dispavg.grid(row=1, column=2, sticky=tk.N)

            best = tk.Label(viewer, text="Meilleur", font=title_font, bg=frame_bg)
            best.grid(row=0, column=3, sticky=tk.S, pady=(10,0))

            dispbest = tk.Label(viewer, text=convert(self.parent.manager.racers[self.parent.manager.racers_id[racer]].best_time()), font=base_font, bg=frame_bg)
            dispbest.grid(row=1, column=3, sticky=tk.N)

            laps = []
            x = []
            y = []
            z = []
            for lap in self.parent.manager.racers[self.parent.manager.racers_id[racer]].laps.values():
                laps.append((lap.time, lap.begin))
                x.append(datetime.datetime.fromtimestamp(lap.begin))
                y.append(lap.time)
                z.append(mean_time)

            count = 1
            for lap in laps:
                out = ("%003d" % count) + ".  " + str(time.strftime("%H:%M", time.localtime(lap[1]))) + "    " + convert(lap[0])
                listbox.insert(tk.END, out)
                count += 1

            fig = Figure()
            ax = fig.add_subplot(111)
            ax.set_title("Historique des temps")
            line1 = ax.plot(x, y, label="Evolution")
            line2 = ax.plot(x, z, label="Moyenne")
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(handles, labels)
            ax.set_xlabel('Heure')
            ax.set_ylabel('Temps')
            fig.autofmt_xdate()
            formatter = matplotlib.ticker.FuncFormatter(lambda s, x: time.strftime('%M:%S', time.gmtime(s)))
            ax.yaxis.set_major_formatter(formatter)

            canvas = FigureCanvasTkAgg(fig, viewer)
            canvas._tkcanvas.grid(row=2, column=2, columnspan=2, sticky=tk.N)
            canvas.show()
            
            center(viewer)

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

        def callback4():
            if len(self.list) == 0:
                return
            if len(self.listbox.curselection()) == 0:
                return
            racer = self.list[self.listbox.curselection()[0]]
            if racer not in self.parent.manager.racers_id:
                return

            viewer = tk.Toplevel(self, bg=frame_bg)
            viewer.title("Modifier coureur")

            name = tk.Entry(viewer, font=base_font)
            name.insert(tk.END, racer)
            name.grid(row=0, column=0, sticky=tk.E)

            def val():
                newracer = name.get()
                newracer = newracer.replace(" ", "_")
                if len(newracer) == 0:
                   return
                if newracer == racer:
                    viewer.destroy()
                if newracer in self.parent.manager.racers_id:
                    return
                self.parent.manager.rename_racer(racer, newracer)
                viewer.destroy()

            validate = tk.Button(viewer, text="OK", command=val, font=button_font)
            validate.grid(row=0, column=1, sticky=tk.W)
            
            center(viewer)

        self.detail = tk.Button(self, text="Détail", command=callback2, font=button_font)
        self.add = tk.Button(self, text="Ajouter", command=callback, font=button_font)
        self.delete = tk.Button(self, text="Supprimer", command=callback3, font=button_font)
        self.modify = tk.Button(self, text="Modifier", command=callback4, font=button_font)

        self.scroll = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.scroll.grid(row=1, column=1, rowspan=4, pady=(0,10), sticky=tk.N+tk.S+tk.W)

        self.listbox = tk.Listbox(self, height=20, width=20, yscrollcommand=self.scroll.set, font=base_font)
        self.listbox.grid(row=1, column=0, rowspan=4, padx=(20, 0), pady=(0,10), sticky=tk.N+tk.S+tk.E)
        self.scroll['command'] = self.listbox.yview
        self.detail.grid(row=4, column=2, sticky=tk.N)
        self.delete.grid(row=2, column=2, padx=20, sticky=tk.N)
        self.add.grid(row=1, column=2, sticky=tk.S)
        self.modify.grid(row=3, column=2, sticky=tk.S)

        self.scroll2 = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.scroll2.grid(row=1, column=4, rowspan=4, padx=(0, 20), pady=(0,10), sticky=tk.N+tk.S+tk.W)

        self.listbox2 = tk.Listbox(self, height=20, width=20, yscrollcommand=self.scroll2.set, font=base_font)
        self.listbox2.grid(row=1, column=3, rowspan=4, pady=(0,10), sticky=tk.N+tk.S+tk.E)
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
        super().__init__(master, bg=frame_bg)
        self.parent = master
        self.name = tk.Label(self, text="Derniers tours", font=title_font, bg=frame_bg)
        self.list = []

        def callback():
            if len(self.list) == 0:
                return
            if len(self.listbox.curselection()) == 0:
                return
            lap = self.list[self.listbox.curselection()[0]]
            
            viewer = tk.Toplevel(self, bg=frame_bg)
            viewer.title("Modifier un tour")

            tk.Label(viewer, text="Coureur", font=title_font, bg=frame_bg).grid(row=0, column=0, sticky=tk.W)
            tk.Label(viewer, text="Temps", font=title_font, bg=frame_bg).grid(row=1, column=0, sticky=tk.W)
            tk.Label(viewer, text=":", bg=frame_bg).grid(row=1, column=2)

            racer = tk.Entry(viewer, font=base_font)
            racer.insert(tk.END, self.parent.manager.racers[lap[1]].name)
            racer.grid(row=0, column=1, columnspan=3)

            mins = tk.Spinbox(viewer, format="%02.0f", from_=0.0, to=59.0, increment=1, width=6, font=base_font)
            secs = tk.Spinbox(viewer, format="%02.0f", from_=0.0, to=59.0, increment=1, width=6, font=base_font)

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

            tk.Button(viewer, text="OK", command=mod, font=button_font).grid(row=0, column=4, rowspan=2)

            mins.grid(row=1, column=1)
            secs.grid(row=1, column=3)
            
            center(viewer)
            
            self.parent.update()

        def callback2():
            if len(self.list) == 0:
                return
            if len(self.listbox.curselection()) == 0:
                return
            lap = self.list[self.listbox.curselection()[0]]
            self.parent.manager.del_lap(lap[1], lap[0])
            self.parent.update()
        
        self.edit = tk.Button(self, text="Modifier", command=callback, font=button_font)       
        self.delete = tk.Button(self, text="Supprimer", command=callback2, font=button_font)

        self.listbox = tk.Listbox(self, height=Manager.LAST_LAPS_SZ, width=20, borderwidth=0, highlightthickness=0, font=base_font)
        self.listbox.grid(row=1, column=0, columnspan=2)
        
        self.name.grid(row=0, column=0, columnspan=2)
        self.edit.grid(row=2, column=0, sticky=tk.E, pady=(0,5))
        self.delete.grid(row=2, column=1, sticky=tk.W, pady=(0,5))

    def update(self):
        index = -1
        if len(self.listbox.curselection()) > 0:
            index = self.listbox.curselection()[0]
            
        self.listbox.delete(0, tk.END)
        for (l_id, r_id) in reversed(self.parent.manager.last_laps):
            racer = self.parent.manager.racers[r_id]
            out = "%s %s" % (convert(racer.laps[l_id].time), racer.name)
            self.listbox.insert(tk.END, out)

        self.list = list(reversed(self.parent.manager.last_laps))

        if index != -1:
            self.listbox.selection_set(index)
            self.listbox.activate(index)

class Timing(tk.Frame):

    def __init__(self, master):
        super().__init__(master, bg=frame_bg)
        self.parent = master

        self.running = False
        
        self.time = tk.Label(self, text=convert(self.parent.manager.timer.elapsed()), font=timer_font, bg=frame_bg)

        def start():
            self.parent.manager.start_lap()
            self.running = True
            self.parent.update()

        def stopstart():
            if not self.running:
                return
            self.parent.manager.end_lap()
            self.parent.update()

        def stop():
            if not self.running:
                return
            self.parent.manager.end_lap()
            self.running = False
            self.parent.update()

        def stay():
            if not self.running:
                return
            self.parent.manager.stay_lap()
            self.parent.update()
        
        self.start = tk.Button(self, text="Start", command=start, font=button_font)
        self.startstop = tk.Button(self, text="Stop & Start", command=stopstart, font=button_font)
        self.stop = tk.Button(self, text="Stop", command=stop, font=button_font)
        self.stay = tk.Button(self, text="Ding ding ding ding ding !", command=stay, font=button_font)
        self.cur = tk.Label(self, bg=frame_bg)
        self.cur.config(text="-", font=cur_font)
        
        self.time.grid(row=1, column=0, columnspan=3)
        self.start.grid(row=2, column=0, sticky=tk.E)
        self.startstop.grid(row=2, column=1)
        self.stop.grid(row=2, column=2, sticky=tk.W)
        self.stay.grid(row=3, column=0, columnspan=3, pady=(0,5))
        self.cur.grid(row=0, column=0, columnspan=3)

    def update(self):
        if self.running:
            self.time.config(text=convert(self.parent.manager.timer.elapsed()))
        else:
            self.time.config(text=convert(0))
        for racer_id in self.parent.manager.queue:
            self.cur.config(text=">>> "+self.parent.manager.racers[racer_id].name+" <<<")
            break

        if len(self.parent.manager.queue) == 0:
            self.cur.config(text="-")

class MainStats(tk.Frame):

    def __init__(self, master):
        super().__init__(master, bg=frame_bg)
        self.parent = master
        self.name = tk.Label(self, text="Stats", font=title_font, bg=frame_bg)
        self.e1 = tk.Label(self, text="Tours", font=base_font, bg=frame_bg)
        self.e2 = tk.Label(self, text=str(self.parent.manager.count), font=base_font, bg=frame_bg)
        self.e3 = tk.Label(self, text="Moyenne", font=base_font, bg=frame_bg)
        self.e4 = tk.Label(self, text=convert(self.parent.manager.mean_time()), font=base_font, bg=frame_bg)

        def callback():
            viewer = tk.Toplevel(self, bg=frame_bg)
            viewer.title("Troupe des Dragons")

            scroll = tk.Scrollbar(viewer, orient=tk.VERTICAL)
            scroll.grid(row=1, column=1, sticky=tk.N+tk.S, pady=(0,10))

            legend = tk.Label(viewer, text=" #     Heure  Temps    Coureur", font=base_font, bg=frame_bg)
            legend.grid(row=0, column=0, sticky=tk.W, padx=(10,0))

            listbox = tk.Listbox(viewer, height=30, width=40, yscrollcommand=scroll.set, borderwidth=0, highlightthickness=0, font=base_font)
            listbox.grid(row=1, column=0, sticky=tk.N+tk.S+tk.E+tk.W, padx=(10,0), pady=(0,10))
            scroll['command'] = listbox.yview

            mean_time = self.parent.manager.mean_time()
            laps = []
            x = []
            y = []
            z = []
            for racer in self.parent.manager.racers.values():
                for lap in racer.laps.values():
                    laps.append((lap.begin, lap.time, racer.name))

            laps.sort()
            count = 1
            for lap in laps:
                out = ("%003d" % count) + ".  " + str(time.strftime("%H:%M", time.localtime(lap[0]))) + "    " + convert(lap[1]) + "     " + lap[2]
                listbox.insert(tk.END, out)
                count += 1
                x.append(datetime.datetime.fromtimestamp(lap[0]))
                y.append(lap[1])
                z.append(mean_time)

            fig = Figure()
            ax = fig.add_subplot(111)
            ax.set_title("Historique des temps")
            line1 = ax.plot(x, y, label="Evolution")
            line2 = ax.plot(x, z, label="Moyenne")
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(handles, labels)
            ax.set_xlabel('Heure')
            ax.set_ylabel('Temps')
            fig.autofmt_xdate()
            formatter = matplotlib.ticker.FuncFormatter(lambda s, x: time.strftime('%M:%S', time.gmtime(s)))
            ax.yaxis.set_major_formatter(formatter)

            canvas = FigureCanvasTkAgg(fig, viewer)
            canvas._tkcanvas.grid(row=0, column=2, rowspan=2)
            canvas.show()
            
            center(viewer)
        
        self.all = tk.Button(self, text="Voir tous les tours", command=callback, font=button_font)

        self.name.grid(row=0, column=0, columnspan=2, sticky=tk.S)
        self.e1.grid(row=1, column=0, sticky=tk.W+tk.S, padx=20)
        self.e2.grid(row=1, column=1, sticky=tk.E+tk.S, padx=20)
        self.e3.grid(row=2, column=0, sticky=tk.W+tk.N, padx=20)
        self.e4.grid(row=2, column=1, sticky=tk.E+tk.N, padx=20)
        self.all.grid(row=3, column=0, columnspan=2, sticky=tk.N)

    def update(self):
        self.e2.config(text=str(self.parent.manager.count))
        self.e4.config(text=convert(self.parent.manager.mean_time()))
        
class TopLaps(tk.Frame):

    def __init__(self, master):
        super().__init__(master, bg=frame_bg)
        self.parent = master
        tk.Label(self, text="Meilleurs tours", font=title_font, bg=frame_bg).grid(row=0, column=0)

        self.listbox = tk.Listbox(self, height=10, width=20, borderwidth=0, highlightthickness=0, state='disabled', disabledforeground='black', font=base_font)
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
        super().__init__(master, bg=frame_bg)
        self.parent = master
        tk.Label(self, text="Nombre de tours", font=title_font, bg=frame_bg).grid(row=0, column=0)

        self.listbox = tk.Listbox(self, height=10, width=20, borderwidth=0, highlightthickness=0, state='disabled', disabledforeground='black', font=base_font)
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
        
        self.manager = Manager()

        self.grid(row=0, column=0, sticky=tk.S+tk.N+tk.E+tk.W)

        self.add_racer = AddRacer(self)
        self.all_racers = AllRacers(self)
        self.last_laps = LastLaps(self)
        self.timing = Timing(self)
        self.main_stats = MainStats(self)
        self.top_laps = TopLaps(self)
        self.top_racers = TopRacers(self)

        # left side
        self.main_stats.grid(row=0, column=0, padx=10, pady=10, sticky=tk.N+tk.S+tk.E+tk.W)
        self.top_laps.grid(row=1, column=0, padx=10, pady=(0,10), sticky=tk.N+tk.S+tk.E+tk.W)
        self.top_racers.grid(row=2, column=0, padx=10, pady=(0,10), sticky=tk.N+tk.S+tk.E+tk.W)

        # center
        self.timing.grid(row=0, column=1, pady=10, sticky=tk.N+tk.S+tk.E+tk.W)
        self.all_racers.grid(row=1, column=1, rowspan=2, pady=(0,10), sticky=tk.N+tk.S+tk.E+tk.W)

        # right side
        self.add_racer.grid(row=0, column=2, padx=10, pady=10, sticky=tk.N+tk.S+tk.E+tk.W)
        self.last_laps.grid(row=1, column=2, rowspan=2, padx=10, pady=(0,10), sticky=tk.N+tk.S+tk.E+tk.W)

        # weights
        top=self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.main_stats.columnconfigure(0, weight=1)
        self.main_stats.columnconfigure(1, weight=1)
        self.main_stats.rowconfigure(0, weight=1)
        self.main_stats.rowconfigure(1, weight=1)
        self.main_stats.rowconfigure(2, weight=1)
        self.main_stats.rowconfigure(3, weight=1)

        self.top_laps.columnconfigure(0, weight=1)
        self.top_laps.rowconfigure(0, weight=1)
        self.top_laps.rowconfigure(1, weight=1)

        self.top_racers.columnconfigure(0, weight=1)
        self.top_racers.rowconfigure(0, weight=1)
        self.top_racers.rowconfigure(1, weight=1)

        self.timing.columnconfigure(0, weight=1)
        self.timing.columnconfigure(1, weight=1)
        self.timing.columnconfigure(2, weight=1)

        self.all_racers.columnconfigure(0, weight=1)
        self.all_racers.columnconfigure(1, weight=1)
        self.all_racers.columnconfigure(2, weight=1)
        self.all_racers.columnconfigure(3, weight=1)
        self.all_racers.columnconfigure(4, weight=1)
        self.all_racers.rowconfigure(0, weight=1)
        self.all_racers.rowconfigure(1, weight=1)
        self.all_racers.rowconfigure(2, weight=1)
        self.all_racers.rowconfigure(3, weight=1)
        self.all_racers.rowconfigure(4, weight=1)

        self.add_racer.columnconfigure(0, weight=1)
        self.add_racer.columnconfigure(1, weight=1)
        self.add_racer.rowconfigure(0, weight=1)
        self.add_racer.rowconfigure(1, weight=1)
        self.add_racer.rowconfigure(2, weight=1)
        self.add_racer.rowconfigure(3, weight=1)

        self.last_laps.columnconfigure(0, weight=1)
        self.last_laps.columnconfigure(1, weight=1)
        self.last_laps.rowconfigure(0, weight=1)
        self.last_laps.rowconfigure(1, weight=1)
        self.last_laps.rowconfigure(2, weight=1)

        self.log_time = time.time()
        
        center(master)

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
        if time.time() - self.log_time > LOG_INTERVAL:
            self.manager.print_log()
            self.log_time = time.time()

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
root.config(bg = bg_color)
gui = GUI(root)
while True:
    try:
        gui.mainloop()
        break
    except UnicodeDecodeError:
        pass

