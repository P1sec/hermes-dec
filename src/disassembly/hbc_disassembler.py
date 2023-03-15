#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Dict, Set, Optional, Any, Sequence
from os.path import dirname, realpath
from argparse import ArgumentParser
from json import dumps
import sys

DISASSEMBLY_DIR = dirname(realpath(__file__))
ROOT_DIR = realpath(DISASSEMBLY_DIR + '/..')
PARSERS_DIR = realpath(ROOT_DIR + '/parsers')
sys.path.insert(0, PARSERS_DIR)

from hbc_bytecode_parser import parse_hbc_bytecode
from hbc_file_parser import HBCReader, StringKind


def do_disassemble(input_file : str):
    
    
    with open(input_file, 'rb') as file_descriptor:

        hbc_reader = HBCReader()

        hbc_reader.read_whole_file(file_descriptor)
        
        """
        output_json_data : Dict[int, dict] = {}
        
        identifier_count = 0
        for string_count, (string_kind, string) in enumerate(zip(hbc_reader.string_kinds, hbc_reader.strings)):
            
            obj = hbc_reader.small_string_table[string_count]
            
            output_json_data[string_count] = {
                'type': {
                    StringKind.String: 'string',
                    StringKind.Identifier: 'identifier',
                    StringKind.Predefined: 'predefined'
                }[string_kind],
                'value': string,
                'is_utf16': bool(obj.isUTF16)
            }
        
        print('{')
        print(',\n'.join(
            '    %d: %s' % (key, dumps(value))
            for key, value in sorted(output_json_data.items())
        ))
        print('}')
        """
        # WIP ..²
        
        # TODO : Print the JSON data generated above, one line per entry I guess?
        
        for function_count, function_header in enumerate(hbc_reader.function_headers):
            # pretty_print_structure(function_header)
            exception_info = ''
            if function_header.hasExceptionHandler:
                exception_data = hbc_reader.function_id_to_exc_handlers[function_count]
                exception_info = '\n  [Exception handlers:'
                for exception_item in exception_data:
                    exception_info += ' [start=' + hex(exception_item.start) + ', '
                    exception_info += 'end=' + hex(exception_item.end) + ', '
                    exception_info += 'target=' + hex(exception_item.target) + ']'
                exception_info += ' ]'
                
            debug_info = ''
            if function_header.hasDebugInfo:
                debug_data = hbc_reader.function_id_to_debug_offsets[function_count]
                debug_info = '\n  [Debug offsets: '
                debug_info += 'source_locs=' + hex(debug_data.source_locations) + ', '
                debug_info += 'lexical_data=' + hex(debug_data.lexical_data) + ']'
                
            print('=> [Function #%d "%s" of %d bytes]: %d params, frame size=%d, env size=%d, read index sz=%d, write index sz=%d, strict=%r, exc handler=%r, debug info=%r  @ offset 0x%08x%s%s' % (
                
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
                
                function_header.offset,
                exception_info,
                debug_info))

            print()
            print('Bytecode listing:')
            print()
            for instruction in parse_hbc_bytecode(function_header, hbc_reader):
                print('==>', repr(instruction))
            print()
            print()
            print('=' * 15)
            print()
            
            # Safety checks:
            assert function_header.unused == 0 and function_header.paramCount < 100


def main():
    
    # TODO : Make an actual CLI with extra options here ..
    
    args = ArgumentParser()
    
    args.add_argument('input_file')
    args.add_argument('output_file', nargs = '?') # , default = '/dev/stdout'
    
    args = args.parse_args()

    if args.output_file:
        stdout = sys.stdout
        with open(args.output_file, 'w', encoding='utf-8') as sys.stdout:
            do_disassemble(args.input_file)
        sys.stdout = stdout
    
        print()
        print('[+] Disassembly output wrote to "%s"' % args.output_file)
        print()
    
    else:
        sys.stdout.reconfigure(encoding='utf-8')
        do_disassemble(args.input_file)
        
if __name__ == '__main__':

    main()
