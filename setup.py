import sys,requests,glob,os
from cx_Freeze import setup, Executable
os.environ['TCL_LIBRARY'] = r'C:\Python36\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\\Python36\tcl\tk8.6'
build_exe_options = {"packages":["queue","tkinter.tix","idna.idnadata"],"include_files":[(requests.certs.where(),'cacert.pem'),"C:/Python36/tcl/tix8.4.3/",("C:/Python36/DLLs/tk86t.dll","tk86t.dll"),("C:/Python36/DLLs/tcl86t.dll","tcl86t.dll")]}
setup(
    name = "BCB",
    version = "1.0",
    options = {"build_exe":build_exe_options},
    description = "Boini Class Viewer",
    executables = [Executable("BCB.py", base = "Win32GUI")])
