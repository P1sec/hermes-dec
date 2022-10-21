#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from re import search, match, findall, sub, finditer, MULTILINE, DOTALL
from typing import List, Dict, Set, Sequence, Union, Optional, Any
from dataclasses import dataclass

from clang.cindex import Index, CursorKind

"""
    This file contains transitory libclang-based code
    that is used for generating structures which have
    been used as a base for the "../parsers/regexp_bytecode_parser.py"
    file, based on the original source code contained within
    the "../original_regex_bytecode_c_src" directory, which
    has been downloaded by the "get_source_codes.sh" script
    contained within the same directory.
    
    It is a scratchpad.
"""


@dataclass
class OpcodeStructureField:
    field_name : str
    field_type : str
    real_type : Optional[str]
    bit_len : Optional[int]

@dataclass
class OpcodeStructure:
    struct_name : str
    fields : List[OpcodeStructureField]

opcode_name_to_structure : Dict[str, OpcodeStructure] = {}
    

def find_typerefs(node, indent = 0, struct : Optional[OpcodeStructure] = None, field : Optional[OpcodeStructureField] = None, visiting_baseclass : bool = False):
    """ Find all references to the type named 'typename'
    """
    # help(node.type)
    # exit()
    # help(node.type.get_declaration())
    # exit()
    print('%sFound `%s` (%s) [line=%s, col=%s] %s' % (
        ' ' * (indent * 2),
        node.spelling, node.kind, node.location.line, node.location.column, (node.type.spelling, node.type.get_canonical().spelling, node.type.get_declaration().underlying_typedef_type.spelling if node.type.get_declaration().kind.is_declaration() else None))) # (node.storage_class, node.type, node.type.spelling, node.translation_unit, node.referenced, node.raw_comment)))
    
    if node.kind == CursorKind.CXX_BASE_SPECIFIER:
        visiting_baseclass = True
    elif node.kind == CursorKind.STRUCT_DECL and ((node.spelling.endswith('Insn') and node.spelling != 'Insn') or 'BracketRange32' in node.spelling):
        struct = OpcodeStructure(node.spelling, [])
        opcode_name_to_structure[node.spelling] = struct
    elif struct and node.kind == CursorKind.FIELD_DECL:
        # help(node)
        # exit()
        field = OpcodeStructureField(node.spelling, node.type.spelling, None, None)
        if node.is_bitfield():
            field.bit_len = node.get_bitfield_width()
        if node.type.get_declaration().kind.is_declaration():
            underlying_type = node.type.get_declaration().underlying_typedef_type.spelling
            if underlying_type and underlying_type != node.spelling and '__' not in underlying_type:
                field.field_type, field.real_type = underlying_type, field.field_type
        struct.fields.append(field)
    elif struct and visiting_baseclass and node.kind == CursorKind.TYPE_REF and node.spelling != 'struct hermes::regex::Insn':
        for otherchild in node.type.get_declaration().get_children():
            find_typerefs(otherchild, indent + 1, struct, field, False)
    # Recurse for children of this node
    for child in node.get_children():
        find_typerefs(child, indent + 1, struct, field, visiting_baseclass)

# INPUT_FILE_NAME = '/home/marin/hermes/include/hermes/Regex/RegexBytecode.h'
INPUT_FILE_NAME = '/home/marin/hermes-dec/parsers/original_regex_bytecode_c_src/RegexBytecode-v0.12.0.h'
# INPUT_FILE_NAME = '/home/marin/hermes-dec/parsers/original_regex_bytecode_c_src/RegexBytecode-v0.0.1.h'

index = Index.create()
tu = index.parse(INPUT_FILE_NAME, args = ['-x', 'c++'])
print('Translation unit:', tu.spelling)
find_typerefs(tu.cursor)

print()
print('=' * 12)
print()
print('=== Decoded structures: ===')
print()

"""
for opcode_name, structure in opcode_name_to_structure.items():
    print('[Struct "%s"]' % opcode_name)
    for field in structure.fields:
        if field.real_type:
            print('    %s %s # %s' % (field.field_type, field.field_name, field.real_type))
        else:
            print('    %s %s' % (field.field_type, field.field_name))
    print()
"""

print()
for opcode_name, structure in opcode_name_to_structure.items():
    print('class %s(LittleEndianStructure):' % opcode_name)
    print('    _pack_ = True')
    if structure.fields:
        print('    _fields_ = [')
        for field_index, field in enumerate(structure.fields):
            readable_type = {
                'bool': 'c_bool',
                'char': 'c_char',
                'char16_t': 'c_wchar',
                'uint8_t': 'c_uint8',
                'uint16_t': 'c_uint16',
                'uint32_t': 'c_uint32'
            }[field.field_type]
            
            if field.bit_len:
                readable_type += ', %d' % field.bit_len
            
            if field.real_type:
                print("        ('%s', %s)%s # %s" % (field.field_name, readable_type, ',' if field_index + 1 < len(structure.fields) else '', field.real_type))
            else:
                print("        ('%s', %s)%s" % (field.field_name, readable_type, ',' if field_index + 1 < len(structure.fields) else ''))
        print('    ]')
    print()

parsed_inst_names = sorted(set(opcode_name.replace('Insn', '') for opcode_name in opcode_name_to_structure.keys()) - {'BracketRange32'})

"""
orig_inst_names = sorted({'Goal', 'LeftAnchor', 'RightAnchor', 'MatchAny', 'U16MatchAny', 'MatchAnyButNewline', 'U16MatchAnyButNewline', 'MatchChar8', 'MatchChar16', 'U16MatchChar32', 'MatchNChar8', 'MatchNCharICase8', 'MatchCharICase8', 'MatchCharICase16', 'U16MatchCharICase32', 'Alternation', 'Jump32', 'Bracket', 'U16Bracket', 'BeginMarkedSubexpression', 'EndMarkedSubexpression', 'BackRef', 'WordBoundary', 'Lookaround', 'BeginLoop', 'EndLoop', 'BeginSimpleLoop', 'EndSimpleLoop', 'Width1Loop'})

print()
print('=>')
print('=> Parsed structures for (len %s):' % len(parsed_inst_names), parsed_inst_names)
print('=> Should match structures (len %s):' % len(orig_inst_names), orig_inst_names)
print()

assert parsed_inst_names == orig_inst_names
"""

print('=')
print()

print('~')
