#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Dict, Set, Sequence, Union, Optional, Any
from io import BytesIO

def read_varint(buf : BytesIO) -> Optional[int]: # From "decodeSLEB128" in the LLVH source code
    
    result = 0
    shift = 0
    byte = None
    
    while True:
        read = buf.read(1)
        if not read:
            break
        byte = read[0]
        result |= (byte & 0x7f) << shift
        shift += 7
        if not byte & 0x80:
            break
    
    if byte is None:
        return None
    
    # Sign-extend and convert if the result is negative
    if byte & 0x40:
        result = int.from_bytes(
            (((-1 << shift) | result) & 0xffffffff_ffffffff).to_bytes(8, 'little', signed = False),
                'little', signed = True)
    
    return result
    
def print_debug_info(buf : BytesIO):
    
    while True:
        function_index = read_varint(buf)
        if function_index is None:
            break
        current_line = read_varint(buf)
        current_column = read_varint(buf)
        
        print()
        print('Function index:', function_index)
        print('Start line:', current_line)
        print('Start column:', current_column)
        
        current_address = 0
        current_statement = 0
        
        while True:
            address_delta = read_varint(buf)
            if address_delta in (-1, None):
                break
            line_delta = read_varint(buf)
            column_delta = read_varint(buf)
            statement_delta = 0
            if line_delta & 1:
                statement_delta = read_varint(buf)
            line_delta >>= 1
            
            current_address += address_delta
            current_line += line_delta
            current_column += column_delta
            current_statement += statement_delta
            
            print('  Address %d: Line %d - Column %d - Statement %d' % (
                current_address, current_line,
                current_column, current_statement))
            
            # print('  Address delta:', address_delta)
            # print('  Line delta:', line_delta)
            # print('  Column delta:', column_delta)
            # print('  Statement delta:', statement_delta)
    
    print()

# WIP ..
