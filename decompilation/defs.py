#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Set, Dict, Tuple, Optional, Sequence, Union, Any
from os.path import dirname, realpath
from sys import path

SCRIPT_DIR = dirname(realpath(__file__))
ROOT_DIR = realpath(SCRIPT_DIR + '/..')
PARSERS_DIR = realpath(ROOT_DIR + '/parsers')

path.append(PARSERS_DIR)

from hbc_file_parser import HBCReader

# TODO... class DecompiledFunctionBody?

class HermesDecompiler:
    
    hbc_reader : HBCReader
    closure_to_caller_function_ids : List[Tuple[int, int]] = {}
    
    function_id_to_body : Dict[int, 'DecompiledFunctionBody']

class DecompiledFunctionBody:
    
    function_name : str
    function_object : object
    
    lines : List['FlowComponent']
    
    #XX
    pass # WIP ..
    

class FlowComponent:
    
    reads_registers : Optional[Set[int]]
    string_index_referencing_register_variables : Optional[Set[int]]
    side_mutates_registers : Optional[Set[int]] # Register assignments other than setting "self.assigns_to_register", e.g in a "for" or "if" statement
    
    pass # WIP

class BlockStart(FlowComponent):

    pass # WIP

class BlockEnd(FlowComponent):
    
    pass # WIP

class JumpTarget(FlowComponent):
    
    pass # Used to make labels, should be retargeted later

class AtomicFlowStatement(FlowComponent):
    # This may assign to a register (at at most function_header.), a global variable, a table array index:
    
    assigns_to_register : Optional[int]
    assigns_to_global_var : Optional[str]  

    assignment_string : str # The Javascript expression (including the left-hand) that should assign to the any of self.assigns_to_register to self.assigns_to_global_var, if present, or an array index of it, or just executed.
    registers_referenced_at_in_assignment_string : List[Tuple[int, int, int, bool]] # (start, end, register_id, is_lefthanded) tuples indicating where register numbers in the form "r0" are referenced in self.assignment_string.

    pass # WIP 

# WIP .. .


