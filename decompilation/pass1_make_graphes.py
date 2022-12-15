#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Tuple, Dict, Set, Sequence, Union, Optional, Any
from os.path import dirname, realpath
from collections import defaultdict
import sys

from defs import HermesDecompiler, DecompiledFunctionBody

SCRIPT_DIR = dirname(realpath(__file__))
GRAPH_TRAVERSERS_DIR = realpath(SCRIPT_DIR + '/graph_traversers')
sys.path.append(GRAPH_TRAVERSERS_DIR)

from step1_generate_call_flow_graph import fill_basic_blocks_into_function
from step2_visit_code_paths import make_code_paths_from_function

class Pass1MakeGraphes:

    def __init__(self, state : HermesDecompiler):
        
        closure_to_caller_function_ids : Dict[Tuple[int, int]] = {}
        
        state.function_id_to_body = {}
        
        for function_count, function_header in enumerate(state.hbc_reader.function_headers):
            
            function_body = DecompiledFunctionBody()
            function_body.function_id = function_count
            function_body.function_name = state.hbc_reader.strings[function_header.functionName]
            function_body.function_object = function_header
            function_body.addr_to_instruction = {}
            function_body.ret_anchors = {}
            function_body.throw_anchors = {}
            function_body.jump_anchors = {}
            function_body.jump_targets = set()
            
            function_body.try_starts = defaultdict(list)
            function_body.try_ends = defaultdict(list)
            function_body.catch_targets = defaultdict(list)
            if function_body.function_object.hasExceptionHandler:
                for handler_count, handler in enumerate(state.hbc_reader.function_id_to_exc_handlers[function_count]):
                    function_body.try_starts[handler.start].append('try_start%d' % handler_count)
                    function_body.try_ends[handler.end].append('try_end%d' % handler_count)
                    function_body.catch_targets[handler.target].append('catch_target%d' % handler_count)

            state.function_id_to_body[function_count] = function_body
            
            for instruction in state.hbc_reader.function_ops[function_count]:
                
                function_body.addr_to_instruction[instruction.original_pos] = instruction
                
                if instruction.inst.name in ('CreateClosure', 'CreateClosureLongIndex',
                    'CreateGeneratorClosure', 'CreateGeneratorClosureLongIndex',
                    'CreateGenerator', 'CreateGeneratorLongIndex', # Generators are actually function bodies nested into generator closures in the HBC generated structures
                    'CreateAsyncClosure', 'CreateAsyncClosureLongIndex'):
                    
                    source_function_id = function_count
                    target_function_id = instruction.arg3
                    
                    assert target_function_id not in closure_to_caller_function_ids
                    closure_to_caller_function_ids[target_function_id] = source_function_id
                
                elif (instruction.inst.name[0] == 'J' or
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
        
            # Do the actual most of the graph-based processing, in order to generate
            # basic blocks, a call flow graph, pre-compute code paths and detect
            # loops, conditional structures, etc. in the code:
            
            fill_basic_blocks_into_function(function_body, state)
            
            make_code_paths_from_function(function_body, state)
            
        state.closure_to_caller_function_ids = closure_to_caller_function_ids
        
        # TODO more steps are to be implemented here...
        
