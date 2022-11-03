#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Tuple, Dict, Set, Sequence, Union, Optional, Any
from os.path import dirname, realpath

from defs import HermesDecompiler

class Pass1MakeGraphes:

    def __init__(self, state : HermesDecompiler):
        
        closure_to_caller_function_ids : Dict[Tuple[int, int]] = {}
        
        for function_count, function_header in enumerate(state.hbc_reader.function_headers):
            
            for instruction in state.hbc_reader.function_ops[function_count]:
                
                if instruction.inst.name in ('CreateClosure', 'CreateClosureLongIndex'):
                    
                    source_function_id = function_count
                    target_function_id = instruction.arg3
                    
                    assert target_function_id not in closure_to_caller_function_ids
                    closure_to_caller_function_ids[target_function_id] = source_function_id
        
        state.closure_to_caller_function_ids = closure_to_caller_function_ids
                    
        
