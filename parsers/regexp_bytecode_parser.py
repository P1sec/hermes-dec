#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from ctypes import LittleEndianStructure, c_bool, c_char, c_wchar, c_uint8, c_uint16, c_uint32
from typing import List, Set, Sequence, Tuple, Any, Union, Dict, Optional
from logging import log, getLogger, DEBUG
from dataclasses import dataclass
from enum import IntEnum, IntFlag
from io import BytesIO
from re import sub

from pretty_print import pretty_print_structure

getLogger().setLevel(DEBUG)


"""
    The RegExp bytecode format is a custom format
    defined here:
        https://github.com/facebook/hermes/blob/v0.12.0/include/hermes/Regex/RegexBytecode.h
        https://github.com/facebook/hermes/blob/v0.12.0/include/hermes/Regex/RegexOpcodes.def
    
    Serialization code is provided here:
        https://github.com/facebook/hermes/blob/v0.12.0/lib/Support/RegExpSerialization.cpp#L282
    
"""

"""
    Additions to the format to note:

    Introduced in bytecode version 66 (version 0.3.0):
    https://github.com/facebook/hermes/commit/201bab747c200c31503b65e6d91db6b5ccda585b
    https://github.com/facebook/hermes/commit/892bf2cf461bfcaea117826ef06a965b1f67e658
            
        Emit Unicode bracket nodes
            REOP(U16Bracket)

        Emit Unicode-flavored instructions
            REOP(U16MatchCharICase32)
            REOP(U16MatchChar32)
            REOP(U16MatchAnyButNewline)
    
    Introduced in bytecode version 60 (version 0.1.1):
    https://github.com/facebook/hermes/commit/87334592a86a119e3618f8c514bb60badf84f2f4

    Optimize matching multiple literal characters
        REOP(MatchNChar8)
        REOP(MatchNCharICase8)
    
    Introduced in bytecode version 74 (version 0.4.0): https://github.com/facebook/hermes/commit/968a809749ac5c727c0fcbdaaa5fa113592f282d

    Implement RegExp dotall flag.
        REOP(MatchAny)
        REOP(U16MatchAny)
"""

class SyntaxFlags(IntFlag):
    ICASE = 1 << 0
    GLOBAL = 1 << 1 # NOSUBS until version 0.3.0. GLOBAL was added in 0.6.0.
    MULTILINE = 1 << 2
    UNICODE = 1 << 3 # UNICODE, later shorteneted to UCODE was added in version 0.3.0.
    DOTALL = 1 << 4 # DOTALL was added in version 0.4.0.
    STICKY = 1 << 5 # STICKY was added in version 0.6.0.

class MatchConstraintSet(IntFlag):
    MatchConstraintNonASCII = 1 << 0 # Requirement: contain 1 char value > 127
    MatchConstraintAnchoredAtStart = 1 << 1 # Requirement: match at pos 0
    MatchConstraintNonEmpty = 1 << 2 # Requirement: contain at least 1 char

MIN_BC_VERSION = 51

class RegexBytecodeHeader(LittleEndianStructure):
    _pack_ = True
    _fields_ = [
        ('markedCount', c_uint16),
        ('loopCount', c_uint16),
        ('syntaxFlags', c_uint8), # Enum: SyntaxFlags
        ('constraints', c_uint8) # Enum: MatchConstraintSet
    ]

def get_opcodes_enum(bytecode_version : int):
    
    # From https://github.com/facebook/hermes/blob/v0.12.0/include/hermes/Regex/RegexOpcodes.def
    
    opcode_name_and_min_version : List[Tuple[str, int]] = [
        ('Goal', MIN_BC_VERSION),
        ('LeftAnchor', MIN_BC_VERSION),
        ('RightAnchor', MIN_BC_VERSION),
        ('MatchAny', 74), # Version 0.4.0
        ('U16MatchAny', 74), # Version 0.4.0
        ('MatchAnyButNewline', MIN_BC_VERSION),
        ('U16MatchAnyButNewline', 66), # Version 0.3.0
        ('MatchChar8', MIN_BC_VERSION),
        ('MatchChar16', MIN_BC_VERSION),
        ('U16MatchChar32', 66), # Version 0.3.0
        ('MatchNChar8', 60), # Version 0.1.1
        ('MatchNCharICase8', 60), # Version 0.1.1
        ('MatchCharICase8', MIN_BC_VERSION),
        ('MatchCharICase16', MIN_BC_VERSION),
        ('U16MatchCharICase32', 66), # Version 0.3.0
        ('Alternation', MIN_BC_VERSION),
        ('Jump32', MIN_BC_VERSION),
        ('Bracket', MIN_BC_VERSION),
        ('U16Bracket', 66), # Version 0.3.0
        ('BeginMarkedSubexpression', MIN_BC_VERSION),
        ('EndMarkedSubexpression', MIN_BC_VERSION),
        ('BackRef', MIN_BC_VERSION),
        ('WordBoundary', MIN_BC_VERSION),
        ('Lookaround', MIN_BC_VERSION), # Previously Lookahead
        ('BeginLoop' if bytecode_version >= 79 else 'BeginLoopPre79', MIN_BC_VERSION),
        ('EndLoop', MIN_BC_VERSION),
        ('BeginSimpleLoop', MIN_BC_VERSION),
        ('EndSimpleLoop', MIN_BC_VERSION),
        ('Width1Loop', MIN_BC_VERSION)
    ]
        
    Opcodes = IntEnum('Opcodes', [
        opcode_name
        for opcode_name, min_version
        in opcode_name_and_min_version
        if bytecode_version >= min_version
    ], start = 0)
    
    # WIP..
        
    return Opcodes

# The following structures have originally been generated
# by the "../code_parsers/bytecode_structs_parser.py"


class GoalInsn(LittleEndianStructure):
    _pack_ = True

class LeftAnchorInsn(LittleEndianStructure):
    _pack_ = True

class RightAnchorInsn(LittleEndianStructure):
    _pack_ = True

class MatchAnyInsn(LittleEndianStructure):
    _pack_ = True

class U16MatchAnyInsn(LittleEndianStructure):
    _pack_ = True

class MatchAnyButNewlineInsn(LittleEndianStructure):
    _pack_ = True

class U16MatchAnyButNewlineInsn(LittleEndianStructure):
    _pack_ = True

class MatchChar8Insn(LittleEndianStructure):
    _pack_ = True
    _fields_ = [
        ('c', c_uint8)
    ]

class MatchChar16Insn(LittleEndianStructure):
    _pack_ = True
    _fields_ = [
        ('c', c_uint16)
    ]

class U16MatchChar32Insn(LittleEndianStructure):
    _pack_ = True
    _fields_ = [
        ('c', c_uint32)
    ]

class MatchCharICase8Insn(LittleEndianStructure):
    _pack_ = True
    _fields_ = [
        ('c', c_uint8)
    ]

class MatchCharICase16Insn(LittleEndianStructure):
    _pack_ = True
    _fields_ = [
        ('c', c_uint16)
    ]

class U16MatchCharICase32Insn(LittleEndianStructure):
    _pack_ = True
    _fields_ = [
        ('c', c_uint32)
    ]

class AlternationInsn(LittleEndianStructure):
    _pack_ = True
    _fields_ = [
        ('secondaryBranch', c_uint32), # hermes::regex::JumpTarget32
        ('primaryConstraints', c_uint8), # hermes::regex::MatchConstraintSet
        ('secondaryConstraints', c_uint8) # hermes::regex::MatchConstraintSet
    ]

class Jump32Insn(LittleEndianStructure):
    _pack_ = True
    _fields_ = [
        ('target', c_uint32) # hermes::regex::JumpTarget32
    ]

class BackRefInsn(LittleEndianStructure):
    _pack_ = True
    _fields_ = [
        ('mexp', c_uint16)
    ]

class BracketRange32(LittleEndianStructure):
    _pack_ = True
    _fields_ = [
        ('start', c_uint32),
        ('end', c_uint32)
    ]

class BracketInsn(LittleEndianStructure):
    _pack_ = True
    _fields_ = [
        ('rangeCount', c_uint32),
        ('negate', c_uint8, 1),
        ('positiveCharClasses', c_uint8, 3),
        ('negativeCharClasses', c_uint8, 3)
    ]
    
    brackets : List[BracketRange32]

class U16BracketInsn(LittleEndianStructure):
    _pack_ = True
    _fields_ = [
        ('rangeCount', c_uint32),
        ('negate', c_uint8, 1),
        ('positiveCharClasses', c_uint8, 3),
        ('negativeCharClasses', c_uint8, 3)
    ]
    
    brackets : List[BracketRange32]

class MatchNChar8Insn(LittleEndianStructure):
    _pack_ = True
    _fields_ = [
        ('charCount', c_uint8)
    ]
    
    chars : bytes

class MatchNCharICase8Insn(LittleEndianStructure):
    _pack_ = True
    _fields_ = [
        ('charCount', c_uint8)
    ]
    
    chars : bytes

class WordBoundaryInsn(LittleEndianStructure):
    _pack_ = True
    _fields_ = [
        ('invert', c_bool)
    ]

class BeginMarkedSubexpressionInsn(LittleEndianStructure):
    _pack_ = True
    _fields_ = [
        ('mexp', c_uint16)
    ]

class EndMarkedSubexpressionInsn(LittleEndianStructure):
    _pack_ = True
    _fields_ = [
        ('mexp', c_uint16)
    ]

class LookaroundInsn(LittleEndianStructure):
    _pack_ = True
    _fields_ = [
        ('invert', c_bool),
        ('forwards', c_bool),
        ('constraints', c_uint8), # hermes::regex::MatchConstraintSet
        ('mexpBegin', c_uint16),
        ('mexpEnd', c_uint16),
        ('continuation', c_uint32) # hermes::regex::JumpTarget32
    ]

class BeginLoopInsn(LittleEndianStructure):
    _pack_ = True
    _fields_ = [
        ('loopId', c_uint32),
        ('min', c_uint32),
        ('max', c_uint32),
        ('mexpBegin', c_uint16),
        ('mexpEnd', c_uint16),
        ('greedy', c_bool),
        ('loopeeConstraints', c_uint8), # hermes::regex::MatchConstraintSet
        ('notTakenTarget', c_uint32) # hermes::regex::JumpTarget32
    ]

class BeginLoopPre79Insn(LittleEndianStructure):
    _pack_ = True
    _fields_ = [
        ('loopId', c_uint32),
        ('min', c_uint32),
        ('max', c_uint32),
        ('mexpBegin', c_uint32),
        ('mexpEnd', c_uint32),
        ('greedy', c_bool),
        ('loopeeConstraints', c_uint8), # hermes::regex::MatchConstraintSet
        ('notTakenTarget', c_uint32) # hermes::regex::JumpTarget32
    ]

class EndLoopInsn(LittleEndianStructure):
    _pack_ = True
    _fields_ = [
        ('target', c_uint32) # hermes::regex::JumpTarget32
    ]

class BeginSimpleLoopInsn(LittleEndianStructure):
    _pack_ = True
    _fields_ = [
        ('loopeeConstraints', c_uint8), # hermes::regex::MatchConstraintSet
        ('notTakenTarget', c_uint32) # hermes::regex::JumpTarget32
    ]

class EndSimpleLoopInsn(LittleEndianStructure):
    _pack_ = True
    _fields_ = [
        ('target', c_uint32) # hermes::regex::JumpTarget32
    ]

class Width1LoopInsn(LittleEndianStructure):
    _pack_ = True
    _fields_ = [
        ('loopId', c_uint32),
        ('min', c_uint32),
        ('max', c_uint32),
        ('greedy', c_bool),
        ('notTakenTarget', c_uint32) # hermes::regex::JumpTarget32
    ]

class ParsedRegex:
    
    header : RegexBytecodeHeader
    instructions : List[object]
    
    def __init__(self):
        self.header = None
        self.instructions = []

# These functions are used to escape substrings when decompiling
# Hermes-compiled regular expression.

# For a list of which caracters to escape in EcmaScript regular
# expressions, please see:
# https://262.ecma-international.org/5.1/#sec-15.10.1

REGULAR_ESCAPE_MAP = {
    # Removed: '&~# ', added: '/' and everything
    # non-printable ASCII, compared to Python regular expressions
    char: '\\' + chr(char)
        if char > 0x20
        else repr(chr(char))
    for char in b'()[]{}?*+|^$/\\.' + bytes(char for char in range(0x20))
}
RANGE_ESCAPE_MAP = {
    char: '\\' + chr(char)
        if char > 0x20
        else repr(chr(char))
    for char in b'[]-\\' + bytes(char for char in range(0x20))
}

def escape(string : str):
    return string.translate(REGULAR_ESCAPE_MAP)

def escape_range(string : str):
    return string.translate(RANGE_ESCAPE_MAP)

def parse_regex(bytecode_version : int, input_bytes : BytesIO) -> ParsedRegex:
    
    header = RegexBytecodeHeader()
    input_bytes.readinto(header)
    
    output = ParsedRegex()
    output.header = header
    
    # log(DEBUG, '_') # DEBUG
    # log(DEBUG, '=' * 34) # DEBUG
    # log(DEBUG, 'Parsed header:') # DEBUG
    # pretty_print_structure(header) # DEBUG
    
    opcode_enum = get_opcodes_enum(bytecode_version)
    
    while True:
        original_pos = input_bytes.tell() - 6
    
        next_opcode = input_bytes.read(1)
        if not next_opcode:
            break
        opcode = next_opcode[0]
        
        op_structure = globals()[opcode_enum(opcode).name + 'Insn']()
        input_bytes.readinto(op_structure)
        
        op_structure.original_pos = original_pos

        # log(DEBUG, '=' * 34) # DEBUG
        # log(DEBUG, 'Parsed %r:' % op_structure) # DEBUG
        # pretty_print_structure(op_structure) # DEBUG

        if opcode in (opcode_enum.Bracket, opcode_enum.U16Bracket):
            op_structure.brackets = []
            
            for count in range(op_structure.rangeCount):
                bracket = BracketRange32()
                input_bytes.readinto(bracket)
                op_structure.brackets.append(bracket)
        
        elif opcode in (opcode_enum.MatchNChar8, opcode_enum.MatchNCharICase8):
            op_structure.chars = input_bytes.read(op_structure.charCount)

        output.instructions.append(op_structure)
        
        
        # WIP read the actual structure here ..
    
    return output

def loop_ending_to_string(instruction):
    if instruction.min == 0 and instruction.max == 0xffffffff:
        output = '*'
    elif instruction.min == 0 and instruction.max == 1:
        output = '?'
    elif instruction.min == 1 and instruction.max == 0xffffffff:
        output = '+'
    elif instruction.max == 0xffffffff:
        output = '{%d,}' % instruction.min
    elif instruction.min == instruction.max:
        output = '{%d}' % instruction.min
    else:
        output = '{%d,%d}' % (instruction.min, instruction.max)
    if not instruction.greedy and output in '*+':
        output += '?'
    return output

class CharacterClass(IntFlag):
    
    Digits = 1 << 0
    Spaces = 1 << 1
    Words = 1 << 2

def decompile_regex(regex : ParsedRegex):
    
    output : str = ''
    
    pending_1width_instructions : List[Width1LoopInsn] = []
    pending_beginloop_instructions : List[Union[BeginLoopInst, BeginLoopPre78Inst]] = []
    
    for instruction in regex.instructions:
        
        if isinstance(instruction, BeginMarkedSubexpressionInsn):
            output += '('
        elif isinstance(instruction, EndMarkedSubexpressionInsn):
            output += ')'
        elif (isinstance(instruction, BeginLoopInsn) or
            isinstance(instruction, BeginLoopPre79Insn)):
            output += '(?:'
            pending_beginloop_instructions.append(instruction)
        elif isinstance(instruction, Width1LoopInsn):
            pending_1width_instructions.append(instruction)
            continue
        elif isinstance(instruction, BracketInsn):
            output += '['
            if instruction.negate:
                output += '^'
            for bracket in instruction.brackets:
                if bracket.start == bracket.end:
                    output += escape_range(chr(bracket.start))
                elif bracket.start + 1 == bracket.end:
                    output += escape_range(chr(bracket.start) + chr(bracket.end))
                else:
                    output += escape_range(chr(bracket.start)) + '-' + escape(chr(bracket.end))
            for flag, char in [
                (CharacterClass.Digits, r'\d'),
                (CharacterClass.Spaces, r'\s'),
                (CharacterClass.Words, r'\w')
            ]:
                if instruction.positiveCharClasses & flag:
                    output += char
                    
                if instruction.negativeCharClasses & flag:
                    output += char.upper()
                    
            output += ']'
        elif (isinstance(instruction, MatchAnyInsn) or
            isinstance(instruction, MatchAnyButNewlineInsn) or
            isinstance(instruction, U16MatchAnyInsn) or
            isinstance(instruction, U16MatchAnyButNewlineInsn)):
            output += '.'
        elif isinstance(instruction, LeftAnchorInsn):
            output += '^'
        elif isinstance(instruction, RightAnchorInsn):
            output += '$'
        elif isinstance(instruction, GoalInsn):
            pass # End of RegExp
        elif (isinstance(instruction, MatchChar8Insn) or
            isinstance(instruction, MatchChar16Insn) or
            isinstance(instruction, U16MatchChar32Insn) or
            isinstance(instruction, MatchCharICase8Insn) or
            isinstance(instruction, MatchCharICase16Insn) or
            isinstance(instruction, U16MatchCharICase32Insn)):
            output += escape(chr(instruction.c))
        elif isinstance(instruction, EndLoopInsn):
            output += ')'
            begin_loop_instruction = pending_beginloop_instructions.pop()
            output += loop_ending_to_string(begin_loop_instruction)
        elif isinstance(instruction, AlternationInsn):
            output += '|'
        elif (isinstance(instruction, MatchNChar8Insn) or
            isinstance(instruction, MatchNCharICase8Insn)):
            output += escape(instruction.chars.decode('utf-8'))
        # WIP.. It's almost implemented
        # TODO: Lookaround, loop, backref, jump, word boundary.. . SVG RegexP Usage...
        # Check code conformance and v0.0.1-more recent code conformance...
        # Test CASE;
        #=
        else:
            raise NotImplementedError('Please disassemble opcode: %r' % instruction)
    
        while pending_1width_instructions:
            instruction : Width1LoopInsn = pending_1width_instructions.pop()
            
            output += loop_ending_to_string(instruction)
    
    output = '/%s/' % output.replace('/', '\\/')
    for flag, char in [
        (SyntaxFlags.ICASE, 'i'),
        (SyntaxFlags.GLOBAL, 'g'),
        (SyntaxFlags.MULTILINE, 'm'),
        (SyntaxFlags.UNICODE, 'u'),
        (SyntaxFlags.DOTALL, 's'),
        (SyntaxFlags.STICKY,'y')
    ]:
        if regex.header.syntaxFlags & flag:
            output += char
    
    # TODO : Create a real "test" file from the Hermes test file,
    # and do it for the global .HBC bytecode file header as well...
    
    # For readibility, avoid nesting (?:) and ()
    # when a BeginMarkedSubexpression appears within
    # a BeginLoop instruction:
    output = sub(r'(?<!\\)\(\?:\(' + # Match for "(?:(" not preceded with a "\"
        r'([^)]*?' + # Capture the in-between in "\1"
        r'[^\\])\)\)', # Match for "))" not preceded with a "\"
        r'(\1)' # Replace "(?:(" SOMETHING "))" with "(" SOMETHING ")"
        , output)
    
    # WIP ..
    
    return output
    
    

def format_struct_to_single_line(struct : object) -> str:
    
    output : str = ''
    if hasattr(struct, 'original_pos'):
        output += '(Pos: %d)  ' % struct.original_pos
    
    output += struct.__class__.__name__.replace('Insn', '', 1)
    
    if getattr(struct, '_fields_', None):
        for field in struct._fields_:
            if field[0] == 'syntaxFlags':
                output += ' {%s=%r}' % (field[0],
                    SyntaxFlags(struct.syntaxFlags))
            elif 'constraint' in field[0].lower():
                output += ' {%s=%r}' % (field[0],
                    MatchConstraintSet(getattr(struct, field[0])))
            elif 'charclasses' in field[0].lower():
                output += ' {%s=%r}' % (field[0],
                    CharacterClass(getattr(struct, field[0])))
            else:
                output += ' {%s=%s}' % (field[0], 
                    getattr(struct, field[0]))
    
    if getattr(struct, 'brackets', None):
        for bracket in struct.brackets:
            output += ' {Range: %r-%r}' % (chr(bracket.start), chr(bracket.end))
    
    if getattr(struct, 'chars', None):
        output += ' {Chars: %r}' % struct.chars
    
    # WIP ..
    
    return output + '\n'


def disasm_regex(regex : ParsedRegex) -> str:
    
    output : str = format_struct_to_single_line(regex.header)
    
    # pretty_print_structure(regex.header)
    
    for instruction in regex.instructions:
        
        output += format_struct_to_single_line(instruction)
    
    # WIP ..
    
    return output

    
if __name__ == '__main__':
    
    SAMPLE_REGEXES : List[str] = [
        b"\x02\x00\x01\x00\x03\x04\x13\x00\x00\x11\x10\x00\x00\x00\x00A\x00\x00\x00A\x00\x00\x00C\x00\x00\x00C\x00\x00\x00H\x00\x00\x00H\x00\x00\x00L\x00\x00\x00M\x00\x00\x00Q\x00\x00\x00Q\x00\x00\x00S\x00\x00\x00T\x00\x00\x00V\x00\x00\x00V\x00\x00\x00Z\x00\x00\x00Z\x00\x00\x00a\x00\x00\x00a\x00\x00\x00c\x00\x00\x00c\x00\x00\x00h\x00\x00\x00h\x00\x00\x00l\x00\x00\x00m\x00\x00\x00q\x00\x00\x00q\x00\x00\x00s\x00\x00\x00t\x00\x00\x00v\x00\x00\x00v\x00\x00\x00z\x00\x00\x00z\x00\x00\x00\x14\x00\x00\x13\x01\x00\x1c\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\x01'\x01\x00\x00\x11\x10\x00\x00\x00\x01A\x00\x00\x00A\x00\x00\x00C\x00\x00\x00C\x00\x00\x00H\x00\x00\x00H\x00\x00\x00L\x00\x00\x00M\x00\x00\x00Q\x00\x00\x00Q\x00\x00\x00S\x00\x00\x00T\x00\x00\x00V\x00\x00\x00V\x00\x00\x00Z\x00\x00\x00Z\x00\x00\x00a\x00\x00\x00a\x00\x00\x00c\x00\x00\x00c\x00\x00\x00h\x00\x00\x00h\x00\x00\x00l\x00\x00\x00m\x00\x00\x00q\x00\x00\x00q\x00\x00\x00s\x00\x00\x00t\x00\x00\x00v\x00\x00\x00v\x00\x00\x00z\x00\x00\x00z\x00\x00\x00\x14\x01\x00\x00",
        b'\x00\x00\x07\x00\x03\x04\x1c\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x14\x00\x00\x00\x0c-\x1c\x01\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\x014\x00\x00\x00\x11\x01\x00\x00\x00\x000\x00\x00\x009\x00\x00\x00\x1c\x02\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01H\x00\x00\x00\x0c.\x1c\x03\x00\x00\x00\x01\x00\x00\x00\xff\xff\xff\xff\x01h\x00\x00\x00\x11\x01\x00\x00\x00\x000\x00\x00\x009\x00\x00\x00\x18\x06\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x04\xc6\x00\x00\x00\x0cE\x1c\x04\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\xa9\x00\x00\x00\x11\x02\x00\x00\x00\x00+\x00\x00\x00+\x00\x00\x00-\x00\x00\x00-\x00\x00\x00\x1c\x05\x00\x00\x00\x01\x00\x00\x00\xff\xff\xff\xff\x01\xc1\x00\x00\x00\x11\x00\x00\x00\x00\x02\x19h\x00\x00\x00\x00',
        b'\x02\x00\x02\x00\x00\x00\x18\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x01\x04(\x00\x00\x00\x13\x00\x00\n\x04new_\x14\x00\x00\x19\x00\x00\x00\x00\x13\x01\x00\x1c\x01\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\x01>\x00\x00\x00\x05\x14\x01\x00\x00'
            # WIP .. . )
    ]
    
    print()
    for regex in SAMPLE_REGEXES:
        
        print(disasm_regex(parse_regex(84, BytesIO(regex))))
        print('==> Decompiled:', decompile_regex(parse_regex(84, BytesIO(regex)))) # WIP .. 
        print()
        print() # WIP .. .
    
    # WIP .. 
