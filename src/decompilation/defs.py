#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Set, Dict, Tuple, Optional, Sequence, Union, Any
from os.path import dirname, realpath
from dataclasses import dataclass
from sys import path
from re import sub
import sys

SCRIPT_DIR = dirname(realpath(__file__))
ROOT_DIR = realpath(SCRIPT_DIR + '/..')
PARSERS_DIR = realpath(ROOT_DIR + '/parsers')

path.insert(0, PARSERS_DIR)

from hbc_bytecode_parser import ParsedInstruction, get_builtin_functions
from hbc_file_parser import HBCReader

class HermesDecompiler:
    
    input_file : str
    output_file : Optional[str]

    calldirect_function_ids : Set[int]
    
    hbc_reader : HBCReader
    
    function_header : object # For the function being transformed to dehydrated state
    indent_level : int = 0 # Used while producing decompilation output

# This will store information related to the curly braces that
# will encompass a loop, a condition, a switch...
#
# At a latter stage of decompilation, the latter basic blocks
# should be checked for non-overlap (TODO)
@dataclass
class BasicBlock:
    start_address : int
    end_address : int

@dataclass
class Environment:

    parent_environment : Optional['Environment'] = None
    nesting_quantity : int = 0
    slot_index_to_varname : Dict[int, str] = None

class DecompiledFunctionBody:
    
    is_global : bool # Is this the global function?
    function_name : str
    function_object : object
    exc_handlers : 'HBCExceptionHandlerInfo'
    
    try_starts : Dict[int, List[str]]
    try_ends : Dict[int, List[str]]
    catch_targets : Dict[int, List[str]]
    
    is_closure : bool = False
    is_async : bool = False
    is_generator : bool = False
    
    # Closure variable naming-related attributes:
    parent_environment : Optional[Environment] = None
    environment_id : Optional[int] = None
    local_items : Dict[int, Environment] = {} # {env_register: Environment}
    
    basic_blocks : List[BasicBlock]
    
    jump_targets : Set[int]
    
    statements : List['TokenString']
    
    # Output decompiled code for this function to stdout
    def output_code(self, state : HermesDecompiler):
        output = ''
        
        if not self.is_global: # Don't prototype the global function
            if self.is_async:
                output += 'async '
            output += 'function'
            if self.is_generator:
                output += '*'
            if not (self.is_closure or self.is_generator):
                assert self.function_name
                output += ' ' + self.function_name
            elif self.is_generator:
                output += ' '
            output += '('
            output += ', '.join('a' + str(index)
                for index in range(self.function_object.paramCount - 1))
            # TODO: Handle function arguments properly otherwise
            output += ') {'
            if self.is_closure or self.is_generator:
                if self.function_name:
                    output += ' // Original name: ' + self.function_name
                    if self.environment_id is not None:
                        output += ', environment: r' + str(self.environment_id)
                elif self.environment_id is not None:
                    output += ' // Environment: r' + str(self.environment_id)
            output += '\n'
            state.indent_level += 1
        
        basic_block_starts = [basic_block.start_address
            for basic_block in self.basic_blocks]
        basic_block_ends = [basic_block.end_address
            for basic_block in self.basic_blocks]
        
        sys.stdout.write(output)
        output = ''

        # Process each statement, including nested functions
        
        for statement in self.statements:
            if statement.assembly:
                pos = statement.assembly[0].original_pos
                
                while pos in basic_block_ends:
                    basic_block_ends.pop(basic_block_ends.index(pos))
                    state.indent_level -= 1
                    output += (' ' * (state.indent_level * 4)) + '}\n'
                
                if pos in self.try_starts:
                    for label in self.try_starts[pos]:
                        output += '%s:\n' % label
                if pos in self.try_ends:
                    for label in self.try_ends[pos]:
                        output += '%s:\n' % label
                if pos in self.catch_targets:
                    for label in self.catch_targets[pos]:
                        output += '%s:\n' % label

                if pos in self.jump_targets:
                    output += 'label_%d:\n' % pos
                
                while pos in basic_block_starts:
                    basic_block_starts.pop(basic_block_starts.index(pos))
                    output += (' ' * (state.indent_level * 4)) + '{\n'
                    state.indent_level += 1

                sys.stdout.write(output)
                output = ''
            
            if statement.tokens:
                sys.stdout.write(' ' * (state.indent_level * 4))
                is_for_loop = statement.tokens[:2] == [RawToken('for'), LeftParenthesisToken()]
                while statement.tokens:
                    op = statement.tokens.pop(0)
                    if isinstance(op, FunctionTableIndex):
                        op.closure_decompile(self)
                    else:
                        sys.stdout.write(str(op))
                if is_for_loop:
                    sys.stdout.write('\n')
                else:
                    sys.stdout.write(';\n')
    
        if not self.is_global:
            state.indent_level -= 1
            sys.stdout.write(' ' * (state.indent_level * 4) + '}')
    
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
class BindToken(Token):
    register : int

    def __str__(self):
        return '.bind(r%d)' % self.register

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

    parent_environment : Optional[Environment] = None
    
    def closure_decompile(self, parent_closure : DecompiledFunctionBody):

        # Is this a nested closure?
        # If yes, print its decompiled code
        if (self.is_closure or self.is_generator) and not self.is_builtin:

            import hbc_decompiler
            hbc_decompiler.decompile_function(self.state, self.function_id,
                parent_environment = self.parent_environment,
                environment_id = self.environment_id,
                is_closure = self.is_closure,
                is_generator = self.is_generator,
                is_async = self.is_async)
            return
        
        # Is this a know builtin or named function?
        name = self._name_if_any()
        if name:
            sys.stdout.write(name)
            return
        
        # Is this anything else?
        sys.stdout.write('<Function #%d: %s>' % (
            self.function_id,
            ', '.join(
                '%s: %s' % (key, value)
                for key, value in self.__dict__.items()
                if key != 'state' and value)
            ))
    
    def _name_if_any(self) -> Optional[str]:
        
        if self.is_builtin:
            builtin_functions = get_builtin_functions(self.state.hbc_reader.parser_module)
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


