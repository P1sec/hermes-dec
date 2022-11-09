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

class AssignmentToken(Token):
    pass

class LeftParenthesisToken(Token):
    pass

class RightParenthesisToken(Token):
    pass

class CatchBlockStart(Token):
    pass

class DotAccessorToken(Token):
    pass

@dataclass
class RightHandRegToken(Token):
    register : int

@dataclass
class BuiltinFunctionToken(Token):
    buildit_function_id : int

@dataclass
class FunctionToken(Token):
    function_id : int

@dataclass
class RawToken(Token):
    token : str


# WIP .. .


