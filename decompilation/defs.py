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

from hbc_bytecode_parser import ParsedInstruction, get_builtin_functions
from hbc_file_parser import HBCReader

class HermesDecompiler:
    
    input_file : str
    output_file : Optional[str]
    
    hbc_reader : HBCReader
    closure_to_caller_function_ids : List[Tuple[int, int]] = {}
    
    indent_level : int = 0 # Used while producing decompilation output
    
    function_id_to_body : Dict[int, 'DecompiledFunctionBody']

# This will store information related to the curly braces that
# will encompass a loop, a condition, a switch...
#
# At a latter stage of decompilation, the latter basic blocks
# should be checked for non-overlap (TODO)
@dataclass
class BasicBlock:
    start_address : int
    end_address : int

class DecompiledFunctionBody:
    
    function_id : int
    function_name : str
    function_object : object
    
    is_closure : bool = False
    is_async : bool = False
    is_generator : bool = False
    
    argument_list : 'TODO' # todo
    
    basic_blocks : List[BasicBlock]
    
    jump_targets : Set[int]
    
    statements : List['TokenString']
    
    def stringify(self, state : HermesDecompiler, environment_id = None):
        output = ''
        
        if self.function_id != 0: # Don't prototype the global function
                # or maybe do it for readibility?
            if self.is_async:
                output += 'async '
            output += 'function'
            if self.is_generator:
                output += '*'
            if not self.is_closure:
                assert self.function_name
                output += ' ' + self.function_name
            output += '('
            # TODO: Handle function arguments
            output += ') {'
            if self.is_closure and self.function_name:
                output += ' // Original name: ' + self.function_name
                if environment_id:
                    output += ', environment Id: ' + str(environment_id)
            output += '\n'
            state.indent_level += 1
        
        basic_block_starts = [basic_block.start_address
            for basic_block in self.basic_blocks]
        basic_block_ends = [basic_block.end_address
            for basic_block in self.basic_blocks]
        
        for statement in self.statements:
            if statement.assembly:
                pos = statement.assembly[0].original_pos
                
                while pos in basic_block_ends:
                    basic_block_ends.pop(basic_block_ends.index(pos))
                    state.indent_level -= 1
                    output += (' ' * (state.indent_level * 4)) + '}\n'
                
                if pos in self.jump_targets:
                    output += 'label_%d:\n' % pos
                
                while pos in basic_block_starts:
                    basic_block_starts.pop(basic_block_starts.index(pos))
                    output += (' ' * (state.indent_level * 4)) + '{\n'
                    state.indent_level += 1
                
                # print('===> ', statement)
            
            if statement.tokens:
                output += (' ' * (state.indent_level * 4)) + ''.join(str(op) for op in statement.tokens)
                if statement.tokens[:2] == [RawToken('for'), LeftParenthesisToken()]:
                    output += '\n'
                else:
                    output += ';\n'
    
        if self.function_id != 0:
            state.indent_level -= 1
            output += ' ' * (state.indent_level * 4)
            output += '}'
    
        return output
    
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
    def __str__(self):
        return 'return '

@dataclass
class ThrowDirective(Token):
    def __str__(self):
        return 'throw '

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
    jump_table_address : int
    default_jump_address : int
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
class ForInLoopNextIter(Token):
    next_value_register : int
    obj_props_register : int
    obj_register : int
    iter_index_register : int
    iter_size_register : int

# Used to mark backward jumps (used in loops)
@dataclass
class JumpCondition(Token):
    target_address : int

# Used to mark forward jumps
@dataclass
class JumpNotCondition(Token):
    target_address : int

@dataclass
class FunctionTableIndex(Token):
    function_id : int
    state : HermesDecompiler
    environment_id : Optional[int] = None
    
    is_closure : bool = False
    is_builtin : bool = False
    is_generator : bool = False
    is_async : bool = False
    
    def __post_init__(self):
        
        if not self.is_builtin:
            self.function_body = self.state.function_id_to_body[self.function_id]
            self.function_body.is_closure = self.is_closure
            self.function_body.is_generator = self.is_generator
            self.function_body.is_async = self.is_async
    
    def __repr__(self):
        if self.is_closure and not self.is_builtin:
            return self.function_body.stringify(self.state, self.environment_id)
        name = self._name_if_any()
        return '<Function #%d%s: %s>' % (
            self.function_id,
            ' (%s)' % name if name else '',
            ', '.join(
                '%s: %s' % (key, value)
                for key, value in self.__dict__.items()
                if key != 'state' and value)
            )
    
    def _name_if_any(self) -> Optional[str]:
        
        if self.is_builtin:
            builtin_functions = get_builtin_functions(self.state.hbc_reader.header.version)
            return builtin_functions[self.function_id]
        
        else:
            return self.state.hbc_reader.strings[
                self.state.hbc_reader.function_headers[
                    self.function_id].functionName
            ] or None
            

@dataclass
class RawToken(Token):
    token : str
    
    def __str__(self):
        return self.token




# WIP .. .


