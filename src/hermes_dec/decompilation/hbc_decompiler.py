#!/usr/bin/env python3
# -*- encoding: Utf-8 -*-
from os.path import realpath, dirname
from argparse import ArgumentParser
from traceback import format_exc
from logging import error
import sys

SCRIPT_DIR = dirname(realpath(__file__))
MODULE_DIR = dirname(realpath(SCRIPT_DIR))
SRC_DIR = dirname(realpath(MODULE_DIR))

sys.path.insert(0, SRC_DIR)

from hermes_dec.parsers.hbc_file_parser import HBCReader, FunctionKind
from hermes_dec.decompilation.pass1_set_metadata import pass1_set_metadata
from hermes_dec.decompilation.pass2_transform_code import pass2_transform_code
from hermes_dec.decompilation.pass3_parse_forin_loops import (
    pass3_parse_forin_loops,
)
from hermes_dec.decompilation.pass4_name_closure_vars import (
    pass4_name_closure_vars,
)
from hermes_dec.decompilation.defs import (
    HermesDecompiler,
    FunctionTableIndex,
    DecompiledFunctionBody,
)
from hermes_dec.disassembly.hbc_disassembler import disassemble_function

"""
    Entry points for the Hermes HBC Decompiler
"""

# Decompile a function and its nested closures to the standard
# output, given a parsed Hermes bytecode file and a function ID:


def decompile_function(state: HermesDecompiler, function_id: int, **kwargs):

    dehydrated = DecompiledFunctionBody()

    dehydrated.function_id = function_id
    dehydrated.function_object = state.hbc_reader.function_headers[function_id]
    dehydrated.is_global = (
        function_id == state.hbc_reader.header.globalCodeIndex
    )

    # Used within FunctionTableIndex.closure_decompile to
    # provide extra context about the current function:
    for key, value in kwargs.items():
        setattr(dehydrated, key, value)

    if dehydrated.function_object.kind == FunctionKind.GeneratorFunction:
        dehydrated.is_generator = True
    if dehydrated.function_object.kind == FunctionKind.AsyncFunction:
        dehydrated.is_async = True

    if dehydrated.function_object.hasExceptionHandler:
        dehydrated.exc_handlers = state.hbc_reader.function_id_to_exc_handlers[
            function_id
        ]

    try:
        pass_no = 1
        pass1_set_metadata(state, dehydrated)

        pass_no = 2
        pass2_transform_code(state, dehydrated)

        pass_no = 3
        pass3_parse_forin_loops(state, dehydrated)

        pass_no = 4
        pass4_name_closure_vars(state, dehydrated)

        pass_no = 'output'
        dehydrated.output_code(state)
    except Exception:
        sys.stdout.flush()
        error(
            'Error while decompiling function "%s" (pass %s): %s'
            % (
                state.hbc_reader.strings[
                    dehydrated.function_object.functionName
                ],
                pass_no,
                format_exc(),
            )
        )
        print('==== Falling back to Disassembly ====')
        disassemble_function(
            state.hbc_reader, function_id, dehydrated.function_object
        )


def do_decompilation(state: HermesDecompiler, file_handle):

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

    args.add_argument('input_file')
    args.add_argument('output_file', nargs='?')

    args = args.parse_args()

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
