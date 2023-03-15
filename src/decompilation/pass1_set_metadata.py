#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Tuple, Dict, Set, Sequence, Union, Optional, Any
from os.path import dirname, realpath
from collections import defaultdict

from defs import HermesDecompiler, DecompiledFunctionBody
from hbc_bytecode_parser import parse_hbc_bytecode


def pass1_set_metadata(state : HermesDecompiler, function_body : DecompiledFunctionBody):

    function_body.function_name = state.hbc_reader.strings[function_body.function_object.functionName]
    function_body.basic_blocks = []
    function_body.jump_targets = set()
    
    function_body.try_starts = defaultdict(list)
    function_body.try_ends = defaultdict(list)
    function_body.catch_targets = defaultdict(list)
    if function_body.function_object.hasExceptionHandler:
        for handler_count, handler in enumerate(function_body.exc_handlers):
            function_body.try_starts[handler.start].append('try_start_%d' % handler_count)
            function_body.try_ends[handler.end].append('try_end%d' % handler_count)
            function_body.catch_targets[handler.target].append('catch_target%d' % handler_count)
    
    for instruction in parse_hbc_bytecode(function_body.function_object, state.hbc_reader):
        
        if (instruction.inst.name[0] == 'J' or
            instruction.inst.name.startswith('SaveGenerator')):
            
            function_body.jump_targets.add(instruction.original_pos + instruction.arg1)
        
        elif instruction.inst.name == 'SwitchImm':
            
            function_body.jump_targets.add(instruction.original_pos + instruction.arg3)
            for jump_target in instruction.switch_jump_table:
                function_body.jump_targets.add(jump_target)

