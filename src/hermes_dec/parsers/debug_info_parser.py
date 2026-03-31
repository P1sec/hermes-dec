#!/usr/bin/env python3
# -*- encoding: Utf-8 -*-
from typing import List, Dict, Set, Sequence, Union, Optional, Any
from io import BytesIO


def read_varint(
    buf: BytesIO,
) -> Optional[int]:  # From "decodeSLEB128" in the LLVH source code

    result = 0
    shift = 0
    byte = None

    while True:
        read = buf.read(1)
        if not read:
            break
        byte = read[0]
        result |= (byte & 0x7F) << shift
        shift += 7
        if not byte & 0x80:
            break

    if byte is None:
        return None

    # Sign-extend and convert if the result is negative
    if byte & 0x40:
        result = int.from_bytes(
            (((-1 << shift) | result) & 0xFFFFFFFF_FFFFFFFF).to_bytes(
                8, 'little', signed=False
            ),
            'little',
            signed=True,
        )

    return result


def print_debug_info(buf: BytesIO, version: int):

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
            if version >= 94 and version < 97:
                scope_address = read_varint(buf)
                env_register = read_varint(buf)
            elif version >= 99:
                env_idx = read_varint(buf)
            # TODO: Version 99: Implement parsing envIdx and scopingInfoTable_, cf.
            # https://github.com/facebook/hermes/commits/913d31a/include/hermes/BCGen/HBC/DebugInfo.h
            # https://github.com/facebook/hermes/commit/bdbf40aa917924322edecff542280b638bcc0cb1
            # https://github.com/facebook/hermes/commit/78d81f8b81d74f6f81511f591709cdf76ecd32bd
            # https://github.com/facebook/hermes/commit/dc00631c8d5484fbd07c0e8286a798a9dfc91f0e
            statement_delta = 0
            if line_delta & 1:
                statement_delta = read_varint(buf)
            line_delta >>= 1

            current_address += address_delta
            current_line += line_delta
            current_column += column_delta
            current_statement += statement_delta

            if version >= 94 and version < 97:
                print(
                    '  Address %d: Line %d - Column %d - Statement %d - Scope address %d - Env register %d'
                    % (
                        current_address,
                        current_line,
                        current_column,
                        current_statement,
                        scope_address,
                        env_register,
                    )
                )
            elif version >= 99:
                print(
                    '  Address %d: Line %d - Column %d - Statement %d - Scope table index %d'
                    % (
                        current_address,
                        current_line,
                        current_column,
                        current_statement,
                        env_idx,
                    )
                )
            else:
                print(
                    '  Address %d: Line %d - Column %d - Statement %d'
                    % (
                        current_address,
                        current_line,
                        current_column,
                        current_statement,
                    )
                )

            # print('  Address delta:', address_delta)
            # print('  Line delta:', line_delta)
            # print('  Column delta:', column_delta)
            # print('  Statement delta:', statement_delta)

    print()


# WIP ..
