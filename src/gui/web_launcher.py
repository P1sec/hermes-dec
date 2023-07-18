#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from os.path import dirname, realpath
from threading import Timer
from pathlib import Path
from sys import path

GUI_DIR = dirname(realpath(__file__))
STATIC_DIR = realpath(GUI_DIR + '/static')

path.insert(0, GUI_DIR)

from webbrowser import open_new_tab

home_path = Path(STATIC_DIR + '/index.html').as_uri()

browser_launcher = Timer(1.0, open_new_tab, (home_path, ))
browser_launcher.daemon = True
browser_launcher.start()

from server import main
main()

# WIP ...