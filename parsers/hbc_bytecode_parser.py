#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Dict, Set, Sequence, Union, Optional, Any
from io import BytesIO

# Imports relative to the current directory:
from hbc_opcodes import hbc51, hbc59, hbc60, hbc62, hbc71, hbc74, hbc76, hbc83, hbc84, hbc89
from serialized_literal_parser import unpack_slp_array, SLPArray, SLPValue, TagType
from hbc_opcodes.def_classes import OperandMeaning, Instruction

class ParsedInstruction:
    inst : Instruction
    arg1 : object
    arg2 : object
    arg3 : object
    arg4 : object
    arg5 : object
    arg6 : object
    switch_jump_table : Optional[List[int]]
    original_pos : int
    hbc_reader : 'HBCReader'
    
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
        
        comment = ''
        for operand_index, operand in enumerate(self.inst.operands):
            if operand.operand_meaning:
                operand_value = getattr(self, 'arg%d' % (operand_index + 1))
                if operand.operand_meaning == OperandMeaning.string_id:
                    comment += '  # String: %r (%s)' % (
                        self.hbc_reader.strings[operand_value],
                        self.hbc_reader.string_kinds[operand_value].name
                    )
                    # WIP ..
                elif operand.operand_meaning == OperandMeaning.bigint_id:
                    comment += '  # BigInt: %s' % (
                        self.hbc_reader.bigint_values[operand_value]
                    )
                elif operand.operand_meaning == OperandMeaning.function_id:
                    function_header = self.hbc_reader.function_headers[operand_value]
                    comment += '  # Function: [#%d %s of %d bytes]: %d params @ offset 0x%08x' % (
                        operand_value,
                        self.hbc_reader.strings[function_header.functionName],
                        function_header.bytecodeSizeInBytes,
                        function_header.paramCount,
                        function_header.offset)
            elif operand.operand_type.name in ('Addr8', 'Addr32'):
                operand_value = getattr(self, 'arg%d' % (operand_index + 1))
                comment += '  # Address: %08x' % (self.original_pos + operand_value)
        if self.inst.name in ('NewArrayWithBuffer', 'NewArrayWithBufferLong'):
            comment += '  # Array: [%s]' % ', '.join(unpack_slp_array(
                self.hbc_reader.arrays[self.arg4:], self.arg3).to_strings(self.hbc_reader.strings))
        elif self.inst.name in ('NewObjectWithBuffer', 'NewObjectWithBufferLong'):
            comment += '  # Object: {%s}' % ', '.join('%s: %s' % (key, value)
                for key, value in zip(
                    unpack_slp_array(
                        self.hbc_reader.object_keys[self.arg4:], self.arg3).to_strings(self.hbc_reader.strings),
                    unpack_slp_array(
                        self.hbc_reader.object_values[self.arg5:], self.arg3).to_strings(self.hbc_reader.strings)
                )
            )
        elif self.inst.name in ('CallBuiltin', 'CallBuiltinLong', 'GetBuiltinClosure'):
            builtin_number = self.arg2
            builtin_functions = get_builtin_functions(self.hbc_reader.header.version)
            comment += '  # Built-in function: [#%d %s]' % (builtin_number, builtin_functions[builtin_number])
        elif self.inst.name == 'SwitchImm':
            comment += '  # Jump table: [%s]' % ', '.join('%08x' % value for value in
                self.switch_jump_table)
        
        return f'{"%08x" % self.original_pos}: <{self.inst.name}>: <{", ".join(operands)}>{comment}'

def get_parser(bytecode_version : int) -> 'module':
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
    
    return parser_module

def get_builtin_functions(bytecode_version : int) -> List[str]:
    
    return get_parser(bytecode_version)._builtin_function_names

def parse_hbc_bytecode(buf : BytesIO, file_offset : int, bytecode_version : int, hbc_reader: 'HBCReader') -> List[Instruction]:
    
    output_instructions : List['Instruction'] = []
    
    parser_module = get_parser(bytecode_version)
    
    while True:
        original_pos = buf.tell()
        
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
        result.original_pos = original_pos
        result.hbc_reader = hbc_reader
        
        for operand in ('arg1', 'arg2', 'arg3', 'arg4', 'arg5', 'arg6'):
            if hasattr(structure, operand):
                setattr(result, operand, getattr(structure, operand))
        
        if inst.name == 'SwitchImm':
            result.switch_jump_table = []
            hbc_reader.file_buffer.seek(file_offset + original_pos + structure.arg2)
            hbc_reader.align_over_padding()
            
            for jump_table_entry in range(structure.arg4, structure.arg5 + 1):
                result.switch_jump_table.append(int.from_bytes(
                    hbc_reader.file_buffer.read(4), 'little') + original_pos)
        
        output_instructions.append(result)
        
        # print('==> [i] DEBUG: Read %s...' % result)
    
    return output_instructions
