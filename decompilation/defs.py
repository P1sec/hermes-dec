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

# This will provide the ability to construct a graph of 
# the basic assembly blocks in the disassembled/decompiled
# output 
class BasicBlock:
    start_address : int
    end_address : int
    
    # These flags should indicate whether we have
    # encountered cycling in
    # "graph_traversers/step2_visite_code_paths.py"
    # (which indicates the presence of a loop):
    may_be_cycling_anchor : bool = False
    may_be_cycling_target : bool = False
    
    # These flags delimite blocks that will markSans titre
    # the code not continue into something
    # whichsoever
    is_unconditional_throw_anchor : bool = False
    is_unconditional_return_end : bool = False

    # These flags delimite blocks that have the
    # code to continue somewhere else
    is_unconditional_jump_anchor : bool = False
    is_yield_action_anchor : bool = False
    
    # These flags delimite blocks that
    # should have more than one branching
    # end
    is_conditional_jump_anchor : bool = False
    if_switch_action_anchor : bool = False

    anchor_instruction : Optional[ParsedInstruction] = None
    jump_targets_for_anchor : Optional[List[int]] = None

    # These attributes will be used to build
    # the decompiler's graph structure
    
    child_nodes : List['BasicBlock']
    parent_nodes : List['BasicBlock']
    
    error_handling_child_nodes : List['BasicBlock']
    error_handling_parent_nodes : List['BasicBlock']
    
    # These attributes should be added at steps 3+
    # of the graph traversal process (using
    # instruction pattern maching, etc)
    
    do_expr_at_begin : Optional['XXX_TODO']
    if_expr_at_begin : Optional['XXX_TODO']
    else_if_expr_at_begin : Optional['XXX_TODO']
    else_expr_at_begin : Optional['XXX_TODO']
    switch_expr_at_begin : Optional['XXX_TODO']
    while_expr_at_begin : Optional['XXX_TODO']
    for_expr_at_begin : Optional['XXX_TODO']
    while_expr_at_end_matching_block : Optional['XXX_TODO']
    closing_brace_at_end_matching_block : Optional['XXX_TODO']
    

"""
# Don't know if will use it:
class CodePathComponent:
    
    basic_block : BasicBlock
    
    choice_jump : bool = False # Will be the first represented choice in the flattened graph in case of any non-switch jump
    choice_fallthrough : bool = False # Will be the first represented in the flattened graph case otherwise, and exept in case of switch jump
    choice_switch_default : bool = False 
    choice_switch_nondefault : Optional[int] = None
"""

class CodePath:
    
    components : List[BasicBlock]
    
    is_cyclic_end : bool = False
    is_return_end : bool = False

class DecompiledFunctionBody:
    
    function_id : int
    function_name : str
    function_object : object
    
    addr_to_instruction : Dict[int, ParsedInstruction]
    
    # The following structures will be used to
    # mark the boundaries of the basic block
    # of the code using the addresses they
    # store are integers:
    try_starts : Dict[int, List[str]] # Boundary address associated with a text label
    try_ends : Dict[int, List[str]] # Boundary address associated with a text label
    catch_targets : Dict[int, List[str]] # Boundary address associated with a text label
    
    jump_anchors : Dict[int, ParsedInstruction] # Non-jump address associated with a jump/switch/yield instruction
    ret_anchors : Dict[int, ParsedInstruction] # Unreacheable address associated with a return instruction
    throw_anchors : Dict[int, ParsedInstruction] # Unreacheable address associated with a jump instruction
    jump_targets : Set[int] # Jump target address
    
    # The following flags correspond to general
    # observed properties of the current function:
    is_closure : bool = False
    is_async : bool = False
    is_generator : bool = False
    
    argument_list : 'TODO' # todo
    
    basic_blocks : List[BasicBlock]
    
    possible_code_paths : List[CodePath]
    
    statements : List['TokenString']
    
    def stringify(self, state : HermesDecompiler, environment_id = None):
        output = ''
        
        global_function_index = state.hbc_reader.header.globalCodeIndex # Should be 0
        
        if self.function_id != global_function_index: # Don't prototype the global function
                # or maybe do it for readibility?
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
                    if environment_id is not None:
                        output += ', environment: r' + str(environment_id)
                elif environment_id is not None:
                    output += ' // Environment: r' + str(environment_id)
            output += '\n'
            state.indent_level += 1
        
        basic_blocks_copy = list(self.basic_blocks)
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
                    basic_block = basic_blocks_copy.pop(basic_block_starts.index(pos))
                    basic_block_starts.pop(basic_block_starts.index(pos))
                    output += (' ' * (state.indent_level * 4)) + '{ //%s\n' % (
                        (' Node %d' % pos) +
                        (' - (Cycling point)' if basic_block.may_be_cycling_target else '') +
                        (' - Child nodes: ' + ' '.join(
                            '%d' % other_basic_block.start_address
                            for other_basic_block in basic_block.child_nodes
                        ) if basic_block.child_nodes else '') +
                        (' - Parent nodes: ' + ' '.join(
                            '%d' % other_basic_block.start_address
                            for other_basic_block in basic_block.parent_nodes
                        ) if basic_block.parent_nodes else '') +
                        (' - EH handlers: ' + ' '.join(
                            '%d' % other_basic_block.start_address
                            for other_basic_block in basic_block.error_handling_child_nodes
                        ) if basic_block.error_handling_child_nodes else '') +
                        (' - EH anchors: ' + ' '.join(
                            '%d' % other_basic_block.start_address
                            for other_basic_block in basic_block.error_handling_parent_nodes
                        ) if basic_block.error_handling_parent_nodes else ''))
                    state.indent_level += 1
                
                # print('===> ', statement)
            
            if statement.tokens:
                output += (' ' * (state.indent_level * 4)) + ''.join(str(op) for op in statement.tokens)
                if statement.tokens[:2] == [RawToken('for'), LeftParenthesisToken()]:
                    output += '\n'
                else:
                    output += ';\n'
        
        while len(basic_block_ends) > len(basic_block_starts):
            basic_block_ends.pop(0)
            state.indent_level -= 1
            output += (' ' * (state.indent_level * 4)) + '}\n'
    
        if self.function_id != global_function_index:
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

# Used to mark conditions expressed in a jump-choice case (opposite
# to a fallthrough-choice case), hence negated compared with the
# assembly expression
# Located before the jump-choice case within the abstract
# decompiler IR stream.
@dataclass
class JumpCondition(Token):
    target_address : int

# Used to mark conditions in a fallthrough-choice case
# (opposite to a jump-choice case), hence negated
# compared with the assembly expression
# Located after the corresponding JC tag and expression
# within the abstract decompiler IR stream, and before
# the fallthrough-choice conditional expression content
# within the abstract decompiler IR stream.
@dataclass
class JumpNotCondition(Token):
    def __str__(self):
        
        return ' // Negative variant: '

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
            name = self._name_if_any()
            
            self.function_body = self.state.function_id_to_body[self.function_id]
            self.function_body.is_closure = self.is_closure
            self.function_body.is_generator = self.is_generator
            self.function_body.is_async = self.is_async
    
    def __repr__(self):
        if (self.is_closure or self.is_generator) and not self.is_builtin:
            return self.function_body.stringify(self.state, self.environment_id)
        name = self._name_if_any()
        if name:
            return name
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


