#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Dict, Set, Sequence, Union, Optional, Any
from io import BytesIO

# Imports relative to the current directory:
from hbc_opcodes import hbc51, hbc59, hbc60, hbc62, hbc71, hbc74, hbc76, hbc83, hbc84, hbc89

class ParsedInstruction:
    inst : 'Instruction'
    arg1 : object
    arg2 : object
    arg3 : object
    arg4 : object
    arg5 : object
    arg6 : object
    
    def __repr__(self):
        operands = [
            '%s: %s' % (
                (self.inst.operands[index].operand_meaning.name
                if self.inst.operands[index].operand_meaning
                else self.inst.operands[index].operand_type.name),
                getattr(self, 'arg%d' % (index + 1))
            )
            for index in range(len(self.inst.operands))
        ]
        
        return f'<{self.inst.name}>: <{", ".join(operands)}>'

def parse_hbc_bytecode(buf : BytesIO, bytecode_version : int) -> List['Instruction']:
    
    output_instructions : List['Instruction'] = []
    
    parser_module_tbl = {
        51: hbc51,
        59: hbc59,
        60: hbc60,
        62: hbc62,
        71: hbc71,
        74: hbc74,
        76: hbc76,
        83: hbc83,
        84: hbc84,
        89: hbc89
    }
    
    for min_version in reversed(sorted(parser_module_tbl)):
        if bytecode_version >= min_version:
            parser_module = parser_module_tbl[min_version]
            break
    
    while True:
        opcode = buf.read(1)
        if not opcode:
            break
        opcode = opcode[0]
        
        inst = parser_module._opcode_to_instruction.get(opcode)
        if not inst:
            raise NotImplementedError('Opcode "0x%02x" is currently not implemented within hermes-dec.' % opcode)
            
        structure = inst.structure()
        buf.readinto(structure)
        
        result = ParsedInstruction()
        result.inst = inst
        
        for operand in ('arg1', 'arg2', 'arg3', 'arg4', 'arg5', 'arg6'):
            if hasattr(structure, operand):
                setattr(result, operand, getattr(structure, operand))
        
        output_instructions.append(result)
        
        # print('==> [i] DEBUG: Read %s...' % result)
    
    return output_instructions
