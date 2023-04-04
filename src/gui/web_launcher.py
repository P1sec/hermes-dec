#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from os.path import dirname, realpath
from sys import path

path.insert(0, dirname(realpath(__file__)))

from webbrowser import open_new_tab

open_new_tab('file:///home/marin/hermes-dec/src/gui/static/index.html')

from server import main
main()

# WIP ...