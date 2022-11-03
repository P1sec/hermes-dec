#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from os.path import realpath, dirname
from argparse import ArgumentParser
from sys import path

SCRIPT_DIR = dirname(realpath(__file__))
ROOT_DIR = realpath(SCRIPT_DIR + '/..')
TESTS_DIR = realpath(ROOT_DIR + '/tests')
ASSETS_DIR = realpath(TESTS_DIR + '/assets')

from defs import HermesDecompiler
from pass0_internally_disassemble import Pass0InternallyDisassemble
from pass1_make_graphes import Pass1MakeGraphes
from pass2_make_atomic_flow import Pass2MakeAtomicFlow

"""
    Entry point for the Hermes HBC Decompiler
"""

if __name__ == '__main__':
    
    args = ArgumentParser()
    
    args = args.parse_args()
    
    # WIP .. Instantiate 
    state = HermesDecompiler()
    
    Pass0InternallyDisassemble(state)
    
    Pass1MakeGraphes(state)
    
    Pass2MakeAtomicFlow(state)
    
    # DEBUG:
    print('[DEBUG] => Number of closures in the JS document:', len(state.closure_to_caller_function_ids))
    
    
    # WIP .. Call Pass0 here
    
    # WIP ..
    
