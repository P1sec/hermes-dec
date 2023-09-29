#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from logging import getLogger, debug, DEBUG
from os.path import realpath, dirname
from argparse import ArgumentParser
from datetime import datetime
from time import time
import sys

SCRIPT_DIR = dirname(realpath(__file__))
ROOT_DIR = realpath(SCRIPT_DIR + '/..')
PARSERS_DIR = realpath(ROOT_DIR + '/parsers')

sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, PARSERS_DIR)

from hbc_file_parser import HBCReader
from pass1_set_metadata import pass1_set_metadata
from pass1b_make_basic_blocks import pass1b_make_basic_blocks
from pass1c_visit_code_paths import pass1c_visit_code_paths
from pass2_transform_code import pass2_transform_code
from pass3_parse_forin_loops import pass3_parse_forin_loops
from pass4_name_closure_vars import pass4_name_closure_vars
from defs import HermesDecompiler, FunctionTableIndex, DecompiledFunctionBody

"""
    Entry points for the Hermes HBC Decompiler
"""

# Decompile a function and its nested closures to the standard
# output, given a parsed Hermes bytecode file and a function ID:

def decompile_function(state : HermesDecompiler, function_id : int, **kwargs):

    dehydrated = DecompiledFunctionBody()
    dehydrated.is_closure = True

    dehydrated.function_id = function_id
    dehydrated.function_object = state.hbc_reader.function_headers[function_id]
    dehydrated.is_global = function_id == state.hbc_reader.header.globalCodeIndex

    # Used within FunctionTableIndex.closure_decompile to
    # provide extra context about the current function:
    for key, value in kwargs.items():
        setattr(dehydrated, key, value)

    if dehydrated.function_object.hasExceptionHandler:
        dehydrated.exc_handlers = state.hbc_reader.function_id_to_exc_handlers[function_id]

    debug('')
    debug('[%s] Decompiling function #%d ("%s")...' % (
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        function_id,
        state.hbc_reader.strings[dehydrated.function_object.functionName]
    ))

    for step in [
        pass1_set_metadata,
        pass1b_make_basic_blocks,
        pass1c_visit_code_paths, # <-- Used only for generating the graph
        pass2_transform_code,
        pass3_parse_forin_loops,
        pass4_name_closure_vars
    ]:
        start_time = time()
        step(state, dehydrated)
        debug('[%s]   Ran "%s" in %0.5f seconds...' % (
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            step.__name__,
            time() - start_time
        ))

    dehydrated.output_code(state)
    

def do_decompilation(state : HermesDecompiler, file_handle):

    hbc_reader = HBCReader()
    state.hbc_reader = hbc_reader

    state.hbc_reader.read_whole_file(file_handle)
    
    state.calldirect_function_ids = set()

    global_function_index = state.hbc_reader.header.globalCodeIndex

    state.indent_level = 0
    decompile_function(state, global_function_index)
    print()

    for function_id in sorted(state.calldirect_function_ids):
        decompile_function(state, function_id)
        print()

def main():

    args = ArgumentParser()
    
    args.add_argument('-d', '--debug', action = 'store_true')
    args.add_argument('input_file')
    args.add_argument('output_file', nargs = '?')
    
    args = args.parse_args()

    if args.debug:
        getLogger().setLevel(DEBUG)
    
    state = HermesDecompiler()
    state.input_file = args.input_file
    state.output_file = args.output_file
    
    with open(state.input_file, 'rb') as file_handle:
        if state.output_file:
            stdout = sys.stdout
            with open(state.output_file, 'w', encoding='utf-8') as sys.stdout:
                do_decompilation(state, file_handle)
            sys.stdout = stdout
            
            print()
            print('[+] Decompiled output wrote to "%s"' % state.output_file)
            print() 
        else:
            sys.stdout.reconfigure(encoding='utf-8')
            do_decompilation(state, file_handle)

if __name__ == '__main__':

    main()    
