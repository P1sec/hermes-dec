#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from os.path import dirname, realpath
from sys import path

path.insert(0, dirname(realpath(__file__)))

from src.gui.web_launcher import main

main()
