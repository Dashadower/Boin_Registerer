import sys,requests,glob,os
from cx_Freeze import setup, Executable
build_exe_options = {"packages":["queue","tkinter.tix"],"include_files":[(requests.certs.where(),'cacert.pem'),"tix8.4.3/"]}
setup(
    name = "BCB",
    version = "1.0",
    options = {"build_exe":build_exe_options},
    description = "Boini Class Viewer",
    executables = [Executable("BCB.py", base = "Win32GUI")])