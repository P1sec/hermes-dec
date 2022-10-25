#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from os.path import dirname, realpath
from sys import path

DISASSEMBLY_DIR = dirname(realpath(__file__))
ROOT_DIR = realpath(DISASSEMBLY_DIR + '/..')
PARSERS_DIR = realpath(ROOT_DIR + '/parsers')
path.append(PARSERS_DIR)

from hbc_file_parser import HBCReader

if __name__ == '__main__':
    
    with open('/home/marin/atypikoo_apk/assets/index.android.bundle', 'rb') as file_descriptor:

        hbc_reader = HBCReader()

        hbc_reader.read_whole_file(file_descriptor)
        
        for function_count, function_header in enumerate(hbc_reader.function_headers):
            # pretty_print_structure(function_header)
            print('=> [Function #%d %s of %d bytes]: %d params @ offset 0x%08x' % (
                
                function_count,
                hbc_reader.strings[function_header.functionName],
                function_header.bytecodeSizeInBytes,
                function_header.paramCount,
                function_header.offset))
            
            print()
            print('Bytecode listing:')
            print()
            for instruction in hbc_reader.function_ops[function_count]:
                print('==>', repr(instruction))
            print()
            print()
            print('=' * 15)
            print()
            
            # Safety checks:
            assert function_header.unused == 0 and function_header.paramCount < 100
        
        # WIP ..

