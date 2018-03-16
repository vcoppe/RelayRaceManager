import cx_Freeze
import sys
import matplotlib
import os

os.environ['TCL_LIBRARY'] = r'C:\Users\igazi\AppData\Local\Programs\Python\Python36-32\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\igazi\AppData\Local\Programs\Python\Python36-32\tcl\tk8.6'

base = None

if sys.platform == 'win32':
    base = "Win32GUI"

executables = [cx_Freeze.Executable("gui.py", base=base, icon="logo.ico")]

cx_Freeze.setup(
    name = "Troupe des Dragons",
    options = {"build_exe": {
        "packages":["tkinter","matplotlib","numpy"],
        "include_files":["logo.ico", r"tcl86t.dll", "tk86t.dll"]}},
    version = "0.01",
    description = "Chrono",
    executables = executables
    )
