#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from os.path import realpath, dirname
from argparse import ArgumentParser
import sys

SCRIPT_DIR = dirname(realpath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from defs import HermesDecompiler, FunctionTableIndex
from pass0_internally_disassemble import Pass0InternallyDisassemble
from pass1_make_graphes import Pass1MakeGraphes
from pass2_make_atomic_flow import Pass2MakeAtomicFlow
from pass3_structure_decompiled_flow import Pass3StructureDecompiledFlow

"""
    Entry point for the Hermes HBC Decompiler
"""

def do_decompilation(state : HermesDecompiler):

    Pass0InternallyDisassemble(state)
    
    Pass1MakeGraphes(state)
    
    Pass2MakeAtomicFlow(state)
    
    Pass3StructureDecompiledFlow(state) # WIP ..
    
    # DEBUG:
    print('[DEBUG] => Number of closures in the JS document:', len(state.closure_to_caller_function_ids))
    
    print('=> DEBUG: [Intermediary representation of the decompiled code]')
        
    for function_id, function_body in state.function_id_to_body.items():
        
        if (function_body.is_closure or function_body.is_generator):
            continue
            # Everything except global (function_id=0) actually
            # seems to be a closure, so if in nested mode etc.
        
        state.indent_level = 0
        print()
        print('=> Decompiling function #%d "%s" (at address 0x%08x%s):' % (
            function_id, function_body.function_name,
            function_body.function_object.offset,
            ''.join((', %s: %s' % (
                    (attribute[3:].title(), int(getattr(function_body, attribute))))
                    for attribute in ('is_closure', 'is_async', 'is_generator')
                    if getattr(function_body, attribute)
                ))
            ))
        print()
        print('_' * 37)
        print()
        print(function_body.stringify(state))
        print()
    
    print()
    
    # WIP ..

def main():

    args = ArgumentParser()
    
    args.add_argument('input_file')
    args.add_argument('output_file', nargs = '?')
    
    args = args.parse_args()
    
    # WIP .. Instantiate
    state = HermesDecompiler()
    state.input_file = args.input_file
    state.output_file = args.output_file
    
    if state.output_file:
        stdout = sys.stdout
        with open(state.output_file, 'w', encoding='utf-8') as sys.stdout:
            do_decompilation(state)
        sys.stdout = stdout
        
        print()
        print('[+] Decompiled output wrote to "%s"' % state.output_file)
        print()
    else:
        sys.stdout.reconfigure(encoding='utf-8')
        do_decompilation(state)

if __name__ == '__main__':

    main()    
