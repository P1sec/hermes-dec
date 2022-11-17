#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Set, Dict, Tuple, Optional, Sequence, Union, Any
from os.path import dirname, realpath
from dataclasses import dataclass
from sys import path

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

@dataclass
class LeftHandRegToken(Token):
    register : int

@dataclass
class AssignmentToken(Token):
    pass

@dataclass
class LeftParenthesisToken(Token):
    pass

@dataclass
class RightParenthesisToken(Token):
    pass

@dataclass
class CatchBlockStart(Token):
    arg_register : int

class DotAccessorToken(Token):
    pass

@dataclass
class RightHandRegToken(Token):
    register : int

@dataclass
class GetEnvironmentToken(Token):
    register : int
    nesting_level : int

@dataclass
class NewEnvironmentToken(Token):
    register : int

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



# WIP .. .


