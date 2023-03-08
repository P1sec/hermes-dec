#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from re import search, match, findall, sub, finditer, MULTILINE, DOTALL
from typing import List, Dict, Set, Sequence, Union, Optional, Any
from os.path import dirname, realpath
from dataclasses import dataclass
from html import escape

TOOLS_DIR = dirname(realpath(__file__))
ROOT_DIR = realpath(TOOLS_DIR + '/..')
DOCS_DIR = realpath(ROOT_DIR + '/docs')
PARSERS_DIR = realpath(ROOT_DIR + '/parsers')

GIT_TAGS = 'v0.0.1 v0.0.3 v0.1.0 v0.2.1 hbc70 hbc73 v0.7.0 v0.8.0 v0.8.1 v0.12.0'.split(' ')

OUTPUT_FILE_NAME = DOCS_DIR + '/opcodes_table.html'

class OperandInfo:
    
    # Note for later: the extra information should maybe
    # put into an HTML tooltip (through the "title"
    # attribute) over respective icons, when rendering
    # the table cells regarding the bytecode versions
    # for each opcode and their respective changes
    
    operand_c_type : str
    operand_readable_type : str
    operand_meaning : Optional[str]
    operand_size_bytes : int

# Each column row should be laid in in the form
# of "<raw_opcode> (<struct_size_bytes>)", be
# bold if the structure size has changed from
# the previous version of the colum, display
# more information at hover

class ColumnInfo:
    
    raw_opcode : int
    present : bool
    has_changed_from_previous : bool
    has_ret_target : bool
    struct_size_bytes : int
    operands : List[OperandInfo]
    
    # Scrape comment information, and render it in a
    # separate row/tooltip then?
    plain_text_desc : Optional[str]
    
    def to_html(self):
        
        if self.has_changed_from_previous:
            html = '<td class="changed" '
        else:
            html = '<td '
        
        html += 'title="%s">' % self.plain_text_desc.replace('<br>', '\n')
        
        html += str(self.raw_opcode)
        
        # html += 'op=%s\x0asz=%s' % (
        #     self.raw_opcode,
        #     self.struct_size_bytes
        # )
        
        html += '</td>'
        
        return html

class InstructionRow:
    
    instruction_name : str
    bytecode_version_to_columns : Dict[int, ColumnInfo]

C_TYPE_TO_RAW_SIZE : Dict[str, int] = {
    'int8_t': 1,
    'int32_t': 4,
    'uint8_t': 1,
    'uint16_t': 2,
    'uint32_t': 4,
    'float': 4,
    'double': 8
}

instruction_name_to_row : Dict[str, InstructionRow] = {}

all_bytecode_versions : Set[int] = set()

for git_tag in GIT_TAGS:

    INPUT_FILE_NAME = PARSERS_DIR + '/original_hermes_bytecode_c_src/BytecodeList-%s.def' % git_tag

    INPUT_VERSION_FILE_NAME = PARSERS_DIR + '/original_hermes_bytecode_c_src/BytecodeVersion-%s.h' % git_tag

    with open(INPUT_VERSION_FILE_NAME) as fd:
        version_file_contents = fd.read()
    bytecode_version : int = int(search(r'BYTECODE_VERSION = (\d+)', version_file_contents).group(1))
    
    all_bytecode_versions.add(bytecode_version)

    opcode_count = 0
    
    accumulated_comment : str = ''
    accumulated_comment_was_used : bool = False
    
    readable_type_to_c_type : Dict[str, str] = {}

    with open(INPUT_FILE_NAME) as fd:
        
        input_source = fd.read()
    
    # Backport OPERAND_FUNCTION_ID declarations added with
    # version 0.12.0 (https://github.com/facebook/hermes/commit/c20d7d8)
    # in order to improve disassembly output readability if needed.
    
    if 'OPERAND_FUNCTION_ID(CallDirect, 3)' not in input_source:
        input_source += '''
OPERAND_FUNCTION_ID(CallDirect, 3)
OPERAND_FUNCTION_ID(CreateClosure, 3)
OPERAND_FUNCTION_ID(CreateClosureLongIndex, 3)
'''

        if 'CreateGeneratorClosure' in input_source:
            input_source += '''
OPERAND_FUNCTION_ID(CreateGeneratorClosure, 3)
OPERAND_FUNCTION_ID(CreateGeneratorClosureLongIndex, 3)
'''

        if 'CreateGenerator' in input_source:
            input_source += '''
OPERAND_FUNCTION_ID(CreateGenerator, 3)
OPERAND_FUNCTION_ID(CreateGeneratorLongIndex, 3)
'''

        if 'CreateAsyncClosure' in input_source:
            input_source += '''
OPERAND_FUNCTION_ID(CreateAsyncClosure, 3)
OPERAND_FUNCTION_ID(CreateAsyncClosureLongIndex, 3)
'''
        
    lines : List[str] = input_source.splitlines()
    
    for line in lines:
        
        if not line.strip():
            accumulated_comment_was_used = False
            accumulated_comment = ''
        
        comment_line = match('^///\s*(.+)', line)
        
        if comment_line:
            comment = comment_line.group(1)
            
            if accumulated_comment_was_used:
                accumulated_comment_was_used = False
                accumulated_comment = ''
            accumulated_comment += comment.strip() + '\n'
        
        line = match('^((?:DEFINE|OPERAND)[^(]+?)\((.+?)\)', line)
            
        if line:
            directive, args = line.groups()
            args = args.split(', ')
            
            # print('=>', directive, args)
            
            def define_opcode(instruction_name : str, operand_types : List[str]):
                
                global instruction_name_to_row
                global opcode_count
                global accumulated_comment_was_used
                global accumulated_comment
                    
                instruction_row = instruction_name_to_row.setdefault(instruction_name, InstructionRow())
                instruction_row.instruction_name = instruction_name
                    
                if not getattr(instruction_row, 'bytecode_version_to_columns', None):
                    instruction_row.bytecode_version_to_columns = {}
                
                column_info = ColumnInfo()
                instruction_row.bytecode_version_to_columns[bytecode_version] = column_info
                
                instruction_operands : List[OperandInfo] = []
                
                for operand_readable_type in operand_types:
                    operand_info = OperandInfo()
                    operand_info.operand_meaning = None
                    operand_info.operand_readable_type = operand_readable_type
                    operand_info.operand_c_type = readable_type_to_c_type[operand_readable_type]
                    operand_info.operand_size_bytes = C_TYPE_TO_RAW_SIZE[operand_info.operand_c_type]
                    
                    instruction_operands.append(operand_info)
                
                column_info.has_changed_from_previous = False
                column_info.struct_size_bytes = sum(operand.operand_size_bytes for operand in instruction_operands)
                column_info.present = True
                column_info.raw_opcode = opcode_count
                column_info.operands = instruction_operands
                
                column_info.plain_text_desc = escape(accumulated_comment.strip()).replace('\n', '<br>')
                
                accumulated_comment_was_used = True
                
                opcode_count += 1
            
            if directive.startswith('DEFINE_OPERAND_TYPE'):
                
                readable_type_to_c_type[args[0]] = args[1]
                
            elif directive.startswith('DEFINE_OPCODE'):
                
                define_opcode(args[0], args[1:])
                
            elif directive.startswith('DEFINE_JUMP'):
                args += {
                    'DEFINE_JUMP_1': ['Addr8'],
                    'DEFINE_JUMP_2': ['Addr8', 'Reg8'],
                    'DEFINE_JUMP_3': ['Addr8', 'Reg8', 'Reg8']
                }[directive]
                
                saved_comment = accumulated_comment
                define_opcode(args[0], args[1:])
                
                accumulated_comment = saved_comment
                define_opcode(args[0] + 'Long', ['Addr32'] + args[2:])
            
            elif directive.startswith('DEFINE_RET_TARGET'):

                instruction_row = instruction_name_to_row[args[0]]
                
                column_info = instruction_row.bytecode_version_to_columns[bytecode_version]
                column_info.has_ret_target = True

            elif directive.startswith('OPERAND_'):
                operand_meaning = {
                    'OPERAND_BIGINT_ID': 'bigint_id',
                    'OPERAND_FUNCTION_ID': 'function_id',
                    'OPERAND_STRING_ID': 'string_id'
                }[directive]

                instruction_row = instruction_name_to_row[args[0]]
                
                column_info = instruction_row.bytecode_version_to_columns[bytecode_version]
                column_info.operands[int(args[1]) - 1].operand_meaning = operand_meaning

# Diff each "ColumnInfo" entry contained within an 
# "InstructionRow" object, in order to set a
# boolean value for the "has_changed_from_previous"
# attribute of it


for instruction_name, row in instruction_name_to_row.items():
    
    previous_column : Optional[ColumnInfo] = None
    
    for bytecode_version, column in sorted(row.bytecode_version_to_columns.items()):
                
        column.plain_text_desc = '%s (total size %d)%s' % (
            ', '.join(
                operand.operand_readable_type
                if not operand.operand_meaning
                else '%s (%s)' % (
                    operand.operand_readable_type,
                    operand.operand_meaning
                )
                for operand in column.operands
            ),
            column.struct_size_bytes,
            '<br><br>' + column.plain_text_desc
            if column.plain_text_desc else ''
        )
        
        if previous_column and (
            [operand.__dict__ for operand in previous_column.operands] !=
            [operand.__dict__ for operand in column.operands]
            or column.plain_text_desc != previous_column.plain_text_desc):
            
            column.has_changed_from_previous = True
        
        previous_column = column

out_source = '''<!DOCTYPE html>
<html>
    <head>
        <title>Opcodes table</title>
        <meta charset="utf-8">
        <style>
            table {
                border-collapse: collapse;
                margin: 14px;
            }
            
            th, td {
                padding: 3px;
                border: 1px solid #ccc;
            }
        
            .changed {
                background: #AB3535;
            }
        </style>
    </head>
    <body>
        <h1>Opcodes of the Hermes virtual machine</h1>
        <p>With the opcode byte value indicated respective to each stable version of the React Native Hermes VM bytecode format, as well as the auto-generated documentation from the "BytecodeList.def" file from the Hermes VM source tree.</p>
        <p>This list of opcodes is used by the <a href="https://github.com/P1sec/hermes-dec" target="_blank">hermes-dec</a> open-source reverse engineering project.</p>
        <table>
            <thead>
                <tr>
                    <th>Instruction</th>
                    <th colspan="%s">Bytecode version to opcode</th>
                    <th>Documentation</th>
                </tr>
                <tr>
                    <th></th>
                    %s
                    <th></th>
                </tr>
            </thead>
            <tbody>
''' % (len(all_bytecode_versions),
    ''.join(
    '<th>%s</th>' % tag
    for tag in sorted(all_bytecode_versions)
))


for instruction_name, row in sorted(instruction_name_to_row.items()):
    
    out_source += '''<tr>
        <td>%s</td>''' % instruction_name
    
    for bytecode_version in sorted(all_bytecode_versions):
        if bytecode_version in row.bytecode_version_to_columns:
            column = row.bytecode_version_to_columns[bytecode_version]
            out_source += column.to_html()
        else:
            out_source += '<td></td>'
    
    out_source += '''
        <td>%s</td>
    </tr>''' % column.plain_text_desc
            

out_source += '''    </body>
</html>
'''

with open(OUTPUT_FILE_NAME, 'w', encoding='utf-8') as file_handle:
    
    file_handle.write(out_source)

print()
print('[+]  Wrote File => %s' % OUTPUT_FILE_NAME)

print()
