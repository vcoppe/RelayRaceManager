#!/usr/bin/env python3
import sys
import xlsxwriter
import datetime
from manager import Manager

path = 'logs/PV2018.log'
manager = Manager()

try:
    file = open(path,"r")

    n_racers = int(file.readline()[:-1])

    for i in range(0,n_racers):
        name = file.readline()[:-1]
        racer_id = manager.add_racer(name)

        n_laps = int(file.readline()[:-1])
        for i in range(0,n_laps):
            line = file.readline()[:-1]
            line = line.split()

            begin = float(line[0])
            time = float(line[1])

            manager.add_lap(racer_id, time, begin)
    
    file.close()
except Exception as e:
    print(e)
#except:
#    print("Error: Failed to load data correctly.")
#    sys.exit()

entries = []

for racer in manager.racers.values():
    for lap in racer.laps.values():
        entries.append((datetime.datetime.fromtimestamp(lap.begin), racer.name, lap.time))

entries = sorted(entries)

workbook = xlsxwriter.Workbook('24h vélo 2018 - Petit vélo.xlsx')
worksheet = workbook.add_worksheet('Tous les tours')

bold = workbook.add_format({'bold': 1})
time_format = workbook.add_format({'num_format': 'dd/mm/yy hh:mm:ss'})

worksheet.write('A1', 'Tour', bold)
worksheet.write('B1', 'Heure', bold)
worksheet.write('C1', 'Rouleur', bold)
worksheet.write('D1', 'Temps', bold)

row = 1
for entry in entries:
        worksheet.write(row, 0, row)
        worksheet.write(row, 1, entry[0], time_format)
        worksheet.write_string(row, 2, entry[1])
        worksheet.write(row, 3, entry[2]/86400)

        row += 1

workbook.close()
        
