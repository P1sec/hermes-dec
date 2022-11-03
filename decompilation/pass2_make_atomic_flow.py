#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Tuple, Dict, Set, Sequence, Union, Optional, Any
from os.path import dirname, realpath

from defs import HermesDecompiler

class Pass2MakeAtomicFlow:
    
    def __init__(self, state : HermesDecompiler):
        
        for function_count, function_header in enumerate(state.hbc_reader.function_headers):
            
            for instruction in state.hbc_reader.function_ops[function_count]:
                
                if instruction.inst.name in ('', ''):
                    
                    
        
        # WIP ..
