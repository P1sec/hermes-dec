#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from os.path import dirname, realpath
from argparse import ArgumentParser
import sys

DISASSEMBLY_DIR = dirname(realpath(__file__))
ROOT_DIR = realpath(DISASSEMBLY_DIR + '/..')
PARSERS_DIR = realpath(ROOT_DIR + '/parsers')
TESTS_DIR = realpath(ROOT_DIR + '/tests')
ASSETS_DIR = realpath(TESTS_DIR + '/assets')
sys.path.append(PARSERS_DIR)

from hbc_file_parser import HBCReader


def do_disassemble(input_file : str):
    
    # with open(TESTS_DIR + '/sample.hbc', 'rb') as file_descriptor:
    with open(input_file, 'rb') as file_descriptor:

        hbc_reader = HBCReader()

        hbc_reader.read_whole_file(file_descriptor)
        
        for function_count, function_header in enumerate(hbc_reader.function_headers):
            # pretty_print_structure(function_header)
            print('=> [Function #%d "%s" of %d bytes]: %d params, frame size=%d, env size=%d, read index sz=%d, write index sz=%d, strict=%r, exc handler=%r, debug info=%r  @ offset 0x%08x' % (
                
                function_count,
                hbc_reader.strings[function_header.functionName],
                function_header.bytecodeSizeInBytes,
                function_header.paramCount,
                function_header.frameSize,
                function_header.environmentSize,
                function_header.highestReadCacheIndex,
                function_header.highestWriteCacheIndex,
                function_header.strictMode,
                function_header.hasExceptionHandler,
                function_header.hasDebugInfo,
                
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


if __name__ == '__main__':
    
    # TODO : Make an actual CLI with extra options here ..
    
    args = ArgumentParser()
    
    args.add_argument('input_file') # , default = ASSETS_DIR + '/index.android.bundle')
    args.add_argument('output_file', nargs = '?') # , default = '/dev/stdout'
    
    args = args.parse_args()

    if args.output_file:
        stdout = sys.stdout
        with open(args.output_file, 'w') as sys.stdout:
            do_disassemble(args.input_file)
        sys.stdout = stdout
    
        print()
        print('[+] Disassembly output wrote to "%s"' % args.output_file)
        print()
    
    else:
        do_disassemble(args.input_file)
        
