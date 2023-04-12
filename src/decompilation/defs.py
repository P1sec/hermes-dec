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

# This should encompass the scope for a HBC assembly-level basic
# block (retranscribed as a for(;;) switch { case X: } case in
# the decompiled code, if not matching a particular NestedFrame
# object as defined below)
# This will provide the ability to construct a graph of
# the basic assembly blocks in the disassembled/decompiled
# output
class BasicBlock:
    # File offsets of the basic block in the Hermes bytecode file.
    start_address : int
    end_address : int

    # Individual number of instructions in the basic block
    insn_count : int

    # Number of instructions that will be gone through
    # when taking the longest possible code path to
    # the present basic block without cycling.
    #
    # => Calculated through, for each "parent_nodes",
    # adding up the "insn_count" of each block where
    # "max_acc_insn_weight" is not set with the
    # "max_acc_insn_weight" value of the first block
    # in the ascending block graph where it is set.
    #
    # => For the first/root block of the code graph,
    # this value is 0.
    #
    # => Used for choosing which block should be
    # preferred to be the main branch or the conditional
    # branch in case of if() conditions, etc. (the branch
    # going the block with the largest "max_acc_insn_weight"
    # should be preferred to be main, and the block with
    # the smallest value should be preferred to be conditional)
    max_acc_insn_weight : int = 0

    # State that will be used in "pre_render_graph.py":
    rendered : bool = False
    marked_to_render : bool = False

    # These flags should indicate whether we have
    # encountered cycling in
    # "graph_traversers/step2_visite_code_paths.py"
    # (which indicates the presence of a loop):
    may_be_cycling_anchor : bool = False
    may_be_cycling_target : bool = False
    
    # These flags delimite blocks that will mark
    # the code not continue into something
    # whichsoever
    is_unconditional_throw_anchor : bool = False
    is_unconditional_return_end : bool = False

    # These flags delimite blocks that have exactly
    # one determined branching end
    is_unconditional_jump_anchor : bool = False
    is_yield_action_anchor : bool = False
    
    # These flags delimite blocks that
    # should have more than one branching
    # end
    is_conditional_jump_anchor : bool = False
    if_switch_action_anchor : bool = False

    # When one the flags above are set, this provides
    # insight about the instruction performing the jump
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

    # Whether this basic block should still be visible in the
    # decompiled code (switch this attribute to False when
    # a NestedFrame totally overlaps the concerned block)
    stay_visible : bool = True

# This should encompass the scope for a decompiled code-level
# nesting frame (switch, if, else if, for, while, do... block)
@dataclass
class NestedFrame:
    start_address : int
    end_address : int

    pass # WIP

@dataclass
class Environment:

    parent_environment : Optional['Environment'] = None
    nesting_quantity : int = 0
    slot_index_to_varname : Dict[int, str] = None

class DecompiledFunctionBody:
    
    is_global : bool # Is this the global function?
    function_name : str
    function_id : int
    function_object : object
    exc_handlers : 'HBCExceptionHandlerInfo'
    
    try_starts : Dict[int, List[str]]
    try_ends : Dict[int, List[str]]
    catch_targets : Dict[int, List[str]]
    
    jump_anchors : Dict[int, ParsedInstruction] # Non-jump address associated with a jump/switch/yield instruction
    ret_anchors : Dict[int, ParsedInstruction] # Unreacheable address associated with a return instruction
    throw_anchors : Dict[int, ParsedInstruction] # Unreacheable address associated with a jump instruction
    jump_targets : Set[int] # Jump target address

    instruction_boundaries : List[int] # Offset for each instruction and end of code, the first item is zero

    is_closure : bool = False
    is_async : bool = False
    is_generator : bool = False
    
    # Closure variable naming-related attributes:
    parent_environment : Optional[Environment] = None
    environment_id : Optional[int] = None
    local_items : Dict[int, Environment] = {} # {env_register: Environment}
    
    basic_blocks : List[BasicBlock]
    nested_frames : List[NestedFrame]
    
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
        
        nested_frame_starts = [nested_frame.start_address
            for nested_frame in self.nested_frames]
        nested_frame_ends = [nested_frame.end_address
            for nested_frame in self.nested_frames]

        basic_block_starts = [basic_block.start_address
            for basic_block in self.basic_blocks]
        basic_block_ends = [basic_block.end_address
            for basic_block in self.basic_blocks]
        
        if len(basic_block_starts) > 1:
            output += (' ' * (state.indent_level * 4))
            output += '_fun%d: for(var _fun%d_ip = 0; ; ) switch(_fun%d_ip) {\n' % (
                self.function_id,
                self.function_id,
                self.function_id
            )
            state.indent_level += 1
        
        sys.stdout.write(output)
        output = ''

        # Process each statement, including nested functions
        
        for statement in self.statements:
            if statement.assembly:
                pos = statement.assembly[0].original_pos
                
                while pos in nested_frame_ends:
                    nested_frame_ends.pop(nested_frame_ends.index(pos))
                    state.indent_level -= 1
                    output += (' ' * (state.indent_level * 4)) + '}\n'
                
                if len(basic_block_starts) > 1 and pos in basic_block_starts:
                    output += 'case %d:' % pos

                    if pos in self.try_starts:
                        for label in self.try_starts[pos]:
                            output += ' // %s' % label
                    if pos in self.try_ends:
                        for label in self.try_ends[pos]:
                            output += ' // %s' % label
                    if pos in self.catch_targets:
                        for label in self.catch_targets[pos]:
                            output += ' // %s' % label

                    output += '\n'
                
                while pos in nested_frame_starts:
                    nested_frame_starts.pop(nested_frame_starts.index(pos))
                    output += (' ' * (state.indent_level * 4)) + '{\n'
                    state.indent_level += 1

                sys.stdout.write(output)
                output = ''
            
            if statement.tokens:
                sys.stdout.write(' ' * (state.indent_level * 4))
                is_block = statement.tokens[:2] == [RawToken('for'), LeftParenthesisToken()]
                while statement.tokens:
                    op = statement.tokens.pop(0)
                    if isinstance(op, FunctionTableIndex):
                        op.closure_decompile(self)
                    elif isinstance(op, JumpNotCondition):
                        conditions = ''.join(str(token) for token in statement.tokens)
                        statement.tokens = []
                        if conditions == 'false':
                            sys.stdout.write('_fun%d_ip = %d; continue _fun%d' % (
                                self.function_id,
                                op.target_address,
                                self.function_id
                            ))
                        else:
                            is_block = True
                            sys.stdout.write('if(')
                            if '(' in conditions or ' ' in conditions:
                                sys.stdout.write('!(%s)' % conditions)
                            elif conditions[0] == '!':
                                sys.stdout.write(conditions[1:])
                            else:
                                sys.stdout.write('!' + conditions)
                            sys.stdout.write(') { _fun%d_ip = %d; continue _fun%d }' % (
                                self.function_id,
                                op.target_address,
                                self.function_id
                            ))
                    elif isinstance(op, JumpCondition):
                        conditions = ''.join(str(token) for token in statement.tokens)
                        statement.tokens = []
                        if conditions == 'true':
                            sys.stdout.write('_fun%d_ip = %d; continue _fun%d' % (
                                self.function_id,
                                op.target_address,
                                self.function_id
                            ))
                        else:
                            is_block = True
                            sys.stdout.write('if(')
                            sys.stdout.write(conditions)
                            sys.stdout.write(') { _fun%d_ip = %d; continue _fun%d }' % (
                                self.function_id,
                                op.target_address,
                                self.function_id
                            ))
                    else:
                        sys.stdout.write(str(op))
                if is_block:
                    sys.stdout.write('\n')
                else:
                    sys.stdout.write(';\n')

        if len(basic_block_starts) > 1:
            state.indent_level -= 1
            sys.stdout.write(' ' * (state.indent_level * 4) + '}\n')
    
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
class NewInnerEnvironmentToken(Token):
    dest_register : int
    parent_register : int
    number_of_slots : int

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


