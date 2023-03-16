#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Dict, Set, Sequence, Union, Optional, Iterator, Any
from logging import warning
from io import BytesIO

# Imports relative to the current directory:
from hbc_opcodes import hbc51, hbc58, hbc59, hbc61, hbc62, hbc68, hbc69, hbc70, hbc72, hbc73, hbc76, hbc80, hbc81, hbc82, hbc83, hbc84, hbc85, hbc86, hbc87, hbc89, hbc90
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
    next_pos : int
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
            builtin_functions = get_builtin_functions(self.hbc_reader.parser_module)
            comment += '  # Built-in function: [#%d %s]' % (builtin_number, builtin_functions[builtin_number])
        elif self.inst.name == 'SwitchImm':
            comment += '  # Jump table: [%s]' % ', '.join('%08x' % value for value in
                self.switch_jump_table)
        
        return f'{"%08x" % self.original_pos}: <{self.inst.name}>: <{", ".join(operands)}>{comment}'

def get_parser(bytecode_version : int) -> 'module':
    parser_module_tbl = {
        51: hbc51,
        58: hbc58,
        59: hbc59,
        61: hbc61,
        62: hbc62,
        68: hbc68,
        69: hbc69,
        70: hbc70,
        # Before version 72/0.4.0, the bytecode format used predefined
        # string identifiers (which were removed in commit 63fb517)
        # These are not supported in the current code setup
        72: hbc72,
        73: hbc73,
        76: hbc76,
        80: hbc80,
        81: hbc81,
        82: hbc82,
        83: hbc83,
        84: hbc84,
        85: hbc85,
        86: hbc86,
        87: hbc87,
        89: hbc89,
        90: hbc90,
        91: hbc90,
        # The changes introduced in Hermes bytecode version 92
        # were reverted to the state of version 91 after a few
        # days from their introduction in the Git tree, into a
        # new version 93.
        93: hbc90
    }
    
    if bytecode_version < 72:
        warning('This file uses an ancient Hermes bytecode format, which ' +
            'is not supported.')

    elif bytecode_version == 92 or bytecode_version > 93:
        warning(('Bytecode version %d corresponds to a development or ' +
            'recent version of the Hermes bytecode and is not ' +
            'formally supported by the current tool.') % bytecode_version)

    for min_version in reversed(sorted(parser_module_tbl)):
        if bytecode_version >= min_version:
            parser_module = parser_module_tbl[min_version]
            break
    
    return parser_module

def get_builtin_functions(parser_module : 'module') -> List[str]:
    
    return parser_module._builtin_function_names

# Read and parse the actual bytecode (+ switch tables) for
# a given function header

def parse_hbc_bytecode(function_header : object, hbc_reader : 'HBCReader') -> Iterator[Instruction]:
    
    hbc_reader.file_buffer.seek(function_header.offset)

    buf = BytesIO(hbc_reader.file_buffer.read(function_header.bytecodeSizeInBytes))

    while True:
        original_pos = buf.tell()
        
        opcode = buf.read(1)
        if not opcode:
            break
        opcode = opcode[0]
        
        inst = hbc_reader.parser_module._opcode_to_instruction.get(opcode)
        if not inst:
            raise NotImplementedError('Opcode "0x%02x" is currently not implemented within hermes-dec.' % opcode)
            
        structure = inst.structure()
        buf.readinto(structure)
        
        result = ParsedInstruction()
        result.inst = inst
        result.original_pos = original_pos
        result.next_pos = original_pos + inst.binary_size
        result.hbc_reader = hbc_reader
        
        for operand in ('arg1', 'arg2', 'arg3', 'arg4', 'arg5', 'arg6'):
            if hasattr(structure, operand):
                setattr(result, operand, getattr(structure, operand))
        
        if inst.name == 'SwitchImm':
            result.switch_jump_table = []
            hbc_reader.file_buffer.seek(function_header.offset + original_pos + structure.arg2)
            hbc_reader.align_over_padding()
            
            for jump_table_entry in range(structure.arg4, structure.arg5 + 1):
                result.switch_jump_table.append(int.from_bytes(
                    hbc_reader.file_buffer.read(4), 'little') + original_pos)
        
        yield result
