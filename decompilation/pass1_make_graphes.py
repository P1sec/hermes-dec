#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Tuple, Dict, Set, Sequence, Union, Optional, Any
from os.path import dirname, realpath

from defs import HermesDecompiler, DecompiledFunctionBody

class Pass1MakeGraphes:

    def __init__(self, state : HermesDecompiler):
        
        closure_to_caller_function_ids : Dict[Tuple[int, int]] = {}
        
        state.function_id_to_body = {}
        
        for function_count, function_header in enumerate(state.hbc_reader.function_headers):
            
            function_body = DecompiledFunctionBody()
            function_body.function_id = function_count
            function_body.function_name = state.hbc_reader.strings[function_header.functionName]
            function_body.function_object = function_header
            function_body.basic_blocks = []
            function_body.jump_targets = set()
            
            state.function_id_to_body[function_count] = function_body
            
            for instruction in state.hbc_reader.function_ops[function_count]:
                
                if instruction.inst.name in ('CreateClosure', 'CreateClosureLongIndex',
                    'CreateAsyncClosure', 'CreateAsyncClosureLongIndex'):
                    
                    source_function_id = function_count
                    target_function_id = instruction.arg3
                    
                    assert target_function_id not in closure_to_caller_function_ids
                    closure_to_caller_function_ids[target_function_id] = source_function_id
                
                elif (instruction.inst.name[0] == 'J' or
                      instruction.inst.name.startswith('SaveGenerator')):
                    
                    function_body.jump_targets.add(instruction.original_pos + instruction.arg1)
                
                elif instruction.inst.name == 'SwitchImm':
                    
                    function_body.jump_targets.add(instruction.original_pos + instruction.arg3)
                    for jump_target in instruction.switch_jump_table:
                        function_body.jump_targets.add(jump_target)
        
        state.closure_to_caller_function_ids = closure_to_caller_function_ids
                    
        
