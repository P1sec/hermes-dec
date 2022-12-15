#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from ctypes import LittleEndianStructure, _SimpleCData, sizeof, c_double, c_int8, c_int32, c_uint8, c_uint16, c_uint32
from typing import List, Dict, Sequence, Set, Tuple, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum

class OperandType:
    name : str
    c_type : _SimpleCData
    
    def __init__(self, name : str, c_type : str):
        
        self.name = name
        self.c_type = {
            'int8_t': c_int8,
            'int32_t': c_int32,
            'uint8_t': c_uint8,
            'uint16_t': c_uint16,
            'uint32_t': c_uint32,
            'double': c_double
        }[c_type]

class OperandMeaning(Enum):
    bigint_id = 1
    function_id = 2
    string_id = 3

@dataclass
class Operand:
    operand_type : OperandType
    operand_meaning : Optional[OperandMeaning]

class Instruction:
    name : str
    opcode : int
    operands : List[Operand]
    structure : LittleEndianStructure
    binary_size : int
    has_ret_target : bool
    
    def __init__(self, name : str, opcode : int, args : List[OperandType], module_ref : 'module'):
    
        self.name = name
        self.opcode = opcode
        self.operands = [Operand(arg, None) for arg in args]
        self.has_ret_target = False
        
        module_ref['_instructions'].append(self)
    
        self.structure = type(name, (LittleEndianStructure, ), dict(
            _pack_ = True,
            _fields_ = [
                ('arg%d' % (pos + 1), operand.c_type)
                for pos, operand in enumerate(args)
            ]
        ))
        
        self.binary_size = 1 + sizeof(self.structure)
