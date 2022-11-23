#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Set, Dict, Tuple, Optional, Sequence, Union, Any
from os.path import dirname, realpath
from dataclasses import dataclass
from sys import path
from re import sub

SCRIPT_DIR = dirname(realpath(__file__))
ROOT_DIR = realpath(SCRIPT_DIR + '/..')
PARSERS_DIR = realpath(ROOT_DIR + '/parsers')

path.append(PARSERS_DIR)

from hbc_bytecode_parser import ParsedInstruction
from hbc_file_parser import HBCReader

class HermesDecompiler:
    
    hbc_reader : HBCReader
    closure_to_caller_function_ids : List[Tuple[int, int]] = {}
    
    function_id_to_body : Dict[int, 'DecompiledFunctionBody']

class DecompiledFunctionBody:
    
    function_name : str
    function_object : object
    
    statements : List['TokenString']
    
    #XX
    pass # WIP ..
    
@dataclass
class TokenString:
    tokens : List['Token']
    assembly : ParsedInstruction

class Token:
    pass
    
    # def __str__(self):
    #     return repr(self).replace(self.__class__.__name__,
    #         sub('[^A-Z]', '', self.__class__.__name__), 1)

@dataclass
class ResumeGenerator(Token):
    result_out_reg : int
    return_bool_out_reg : int

@dataclass
class SaveGenerator(Token):
    address : int

@dataclass
class StartGenerator(Token):
    pass

@dataclass
class ReturnDirective(Token):
    register : int

@dataclass
class LeftHandRegToken(Token):
    register : int
    
    def __str__(self):
        return 'r%d' % self.register

@dataclass
class AssignmentToken(Token):
    def __str__(self):
        return ' = '

@dataclass
class LeftParenthesisToken(Token):
    def __str__(self):
        return '('

@dataclass
class RightParenthesisToken(Token):
    def __str__(self):
        return ')'

@dataclass
class CatchBlockStart(Token):
    arg_register : int

@dataclass
class DotAccessorToken(Token):
    def __str__(self):
        return '.'

@dataclass
class RightHandRegToken(Token):
    register : int
    
    def __str__(self):
        return 'r%d' % self.register

@dataclass
class GetEnvironmentToken(Token):
    register : int
    nesting_level : int

@dataclass
class LoadFromEnvironmentToken(Token):
    register : int
    slot_index : int

@dataclass
class NewEnvironmentToken(Token):
    register : int

@dataclass
class SwitchImm(Token):
    value_reg : int
    jump_table_offset : int
    default_jump_offset : int
    unsigned_min_value : int
    unsigned_max_value : int

@dataclass
class StoreToEnvironment(Token):
    env_register : int
    slot_index : int
    value_register : int

@dataclass
class ForInLoopInit(Token):
    obj_props_register : int
    obj_register : int
    iter_index_register : int
    iter_size_register : int

@dataclass
class ForInLoopInit(Token):
    obj_props_register : int
    obj_register : int
    iter_index_register : int
    iter_size_register : int

@dataclass
class ForInLoopNextIter(Token):
    next_value_register : int
    obj_props_register : int
    obj_register : int
    iter_index_register : int
    iter_size_register : int

@dataclass
class JumpConditionToken(Token):
    target_address : int

@dataclass
class FunctionTableIndex(Token):
    function_id : int
    environment_id : Optional[int] = None
    
    is_closure : bool = False
    is_builtin : bool = False
    is_generator : bool = False
    is_async : bool = False

@dataclass
class RawToken(Token):
    token : str
    
    def __str__(self):
        return self.token



# WIP .. .


