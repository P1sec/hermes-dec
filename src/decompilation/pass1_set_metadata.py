#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Tuple, Dict, Set, Sequence, Union, Optional, Any
from os.path import dirname, realpath
from collections import defaultdict

from defs import HermesDecompiler, BasicBlock, DecompiledFunctionBody
from hbc_bytecode_parser import parse_hbc_bytecode


def pass1_set_metadata(state : HermesDecompiler, function_body : DecompiledFunctionBody):

    function_body.function_name = state.hbc_reader.strings[function_body.function_object.functionName]
    function_body.nested_frames = []
    function_body.ret_anchors = {}
    function_body.throw_anchors = {}
    function_body.jump_anchors = {}
    function_body.jump_targets = set()
    
    # Record the addresses for the try_*, catch_* addresses within code

    function_body.try_starts = defaultdict(list)
    function_body.try_ends = defaultdict(list)
    function_body.catch_targets = defaultdict(list)
    if function_body.function_object.hasExceptionHandler:
        for handler_count, handler in enumerate(function_body.exc_handlers):
            function_body.try_starts[handler.start].append('try_start_%d' % handler_count)
            function_body.try_ends[handler.end].append('try_end%d' % handler_count)
            function_body.catch_targets[handler.target].append('catch_target%d' % handler_count)

    # As well as Jump, Switch, Yield

    function_body.instruction_boundaries = []

    for instruction in parse_hbc_bytecode(function_body.function_object, state.hbc_reader):
        
        function_body.instruction_boundaries.append(instruction.original_pos)

        if (instruction.inst.name[0] == 'J' or
            instruction.inst.name.startswith('SaveGenerator')):

            function_body.jump_anchors[instruction.next_pos] = instruction
            function_body.jump_targets.add(instruction.original_pos + instruction.arg1)
        
        elif instruction.inst.name == 'SwitchImm':

            function_body.jump_anchors[instruction.next_pos] = instruction
            function_body.jump_targets.add(instruction.original_pos + instruction.arg3)
            for jump_target in instruction.switch_jump_table:
                function_body.jump_targets.add(jump_target)
        
        elif instruction.inst.name == 'Ret':
            
            function_body.ret_anchors[instruction.next_pos] = instruction
        
        elif instruction.inst.name == 'Throw':
            
            function_body.throw_anchors[instruction.next_pos] = instruction
    
    # Add the end of code offset to "function_body.instruction_boundaries"
    function_body.instruction_boundaries.append(instruction.next_pos
        if function_body.instruction_boundaries else 0)
    
