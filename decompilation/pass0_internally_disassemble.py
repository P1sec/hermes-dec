#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from os.path import dirname, realpath
from sys import path

SCRIPT_DIR = dirname(realpath(__file__))
ROOT_DIR = realpath(SCRIPT_DIR + '/..')
PARSERS_DIR = realpath(ROOT_DIR + '/parsers')
TESTS_DIR = realpath(ROOT_DIR + '/tests')
ASSETS_DIR = realpath(TESTS_DIR + '/assets')

path.append(PARSERS_DIR)

from hbc_file_parser import HBCReader
from defs import HermesDecompiler

class Pass0InternallyDisassemble:
    
    def __init__(self, state : HermesDecompiler):
        
        hbc_reader = HBCReader()
        state.hbc_reader = hbc_reader
    
        # with open(TESTS_DIR + '/sample.hbc', 'rb') as file_handle:
        with open(ASSETS_DIR + '/index.android.bundle', 'rb') as file_handle:
            state.hbc_reader.read_whole_file(file_handle)
        
        
