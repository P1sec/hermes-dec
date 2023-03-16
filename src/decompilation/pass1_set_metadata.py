#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Tuple, Dict, Set, Sequence, Union, Optional, Any
from os.path import dirname, realpath
from collections import defaultdict

from defs import HermesDecompiler, BasicBlock, DecompiledFunctionBody
from hbc_bytecode_parser import parse_hbc_bytecode


def pass1_set_metadata(state : HermesDecompiler, function_body : DecompiledFunctionBody):

    function_body.function_name = state.hbc_reader.strings[function_body.function_object.functionName]
    function_body.nested_frames = []
    function_body.ret_anchors = {}
    function_body.throw_anchors = {}
    function_body.jump_anchors = {}
    function_body.jump_targets = set()
    
    # Record the addresses for the try_*, catch_* addresses within code

    function_body.try_starts = defaultdict(list)
    function_body.try_ends = defaultdict(list)
    function_body.catch_targets = defaultdict(list)
    if function_body.function_object.hasExceptionHandler:
        for handler_count, handler in enumerate(function_body.exc_handlers):
            function_body.try_starts[handler.start].append('try_start_%d' % handler_count)
            function_body.try_ends[handler.end].append('try_end%d' % handler_count)
            function_body.catch_targets[handler.target].append('catch_target%d' % handler_count)

    # As well as Jump, Switch, Yield

    for instruction in parse_hbc_bytecode(function_body.function_object, state.hbc_reader):
        
        if (instruction.inst.name[0] == 'J' or
            instruction.inst.name.startswith('SaveGenerator')):

            function_body.jump_anchors[instruction.next_pos] = instruction
            function_body.jump_targets.add(instruction.original_pos + instruction.arg1)
        
        elif instruction.inst.name == 'SwitchImm':

            function_body.jump_anchors[instruction.next_pos] = instruction
            function_body.jump_targets.add(instruction.original_pos + instruction.arg3)
            for jump_target in instruction.switch_jump_table:
                function_body.jump_targets.add(jump_target)
        
        elif instruction.inst.name == 'Ret':
            
            function_body.ret_anchors[instruction.next_pos] = instruction
        
        elif instruction.inst.name == 'Throw':
            
            function_body.throw_anchors[instruction.next_pos] = instruction
    
    """
        Make basic blocks out of assembly
    """

    error_handlers = (state.hbc_reader.function_id_to_exc_handlers[function_body.function_id]
        if function_body.function_object.hasExceptionHandler else [])
    
    basic_block_boundaries = ({0} |
        function_body.try_starts.keys() | function_body.try_ends.keys() | function_body.catch_targets.keys() |
        function_body.jump_anchors.keys() | function_body.ret_anchors.keys() | function_body.throw_anchors.keys() |
        function_body.jump_targets)
    
    basic_blocks = function_body.basic_blocks = []
    
    start_to_basic_block : Dict[int, BasicBlock] = {}
    end_to_basic_block : Dict[int, BasicBlock] = {}
    
    # Create the basic blocks that will constitute the control
    # flow graph for the current function
    
    basic_block_start = 0
    may_have_fallen_through : bool = False
    for basic_block_end in sorted(basic_block_boundaries)[1:]:
        
        basic_block = BasicBlock()
        basic_block.start_address = basic_block_start
        basic_block.end_address = basic_block_end
        
        start_to_basic_block[basic_block_start] = basic_block
        end_to_basic_block[basic_block_end] = basic_block
        
        basic_block.child_nodes = []
        basic_block.parent_nodes = []
        basic_block.error_handling_child_nodes = []
        basic_block.error_handling_parent_nodes = []
    
        if may_have_fallen_through:
            basic_block.parent_nodes.append(basic_blocks[-1])
            basic_blocks[-1].child_nodes.append(basic_block)
        
        may_have_fallen_through = True
        if basic_block_end in function_body.ret_anchors:
            may_have_fallen_through = False
            basic_block.anchor_instruction = function_body.ret_anchors[basic_block_end]
            basic_block.is_unconditional_return_end = True
        elif basic_block_end in function_body.throw_anchors:
            may_have_fallen_through = False
            basic_block.anchor_instruction = function_body.throw_anchors[basic_block_end]
            basic_block.is_unconditional_throw_anchor = True
        elif basic_block_end in function_body.jump_anchors:
            op = function_body.jump_anchors[basic_block_end]
            basic_block.anchor_instruction = op
            op_name = op.inst.name
            if op_name in ('Jmp', 'JmpLong'):
                may_have_fallen_through = False
                basic_block.jump_targets_for_anchor = [op.original_pos + op.arg1]
                basic_block.is_unconditional_jump_anchor = True
            elif op_name == 'SwitchImm':
                may_have_fallen_through = False
                basic_block.jump_targets_for_anchor = sorted({op.original_pos + op.arg3, *op.switch_jump_table})
                basic_block.if_switch_action_anchor = True
            elif op_name in ('SaveGenerator', 'SaveGeneratorLong'):
                may_have_fallen_through = True
                basic_block.jump_targets_for_anchor = [op.original_pos + op.arg1]
                basic_block.is_yield_action_anchor = True
            elif op_name[0] == 'J':
                may_have_fallen_through = True
                basic_block.jump_targets_for_anchor = [op.original_pos + op.arg1]
                basic_block.is_conditional_jump_anchor = True
            else:
                raise ValueError
        
        basic_blocks.append(basic_block)
    
        basic_block_start = basic_block_end
    
    for basic_block in basic_blocks:
        if basic_block.jump_targets_for_anchor:
            
            # Link graphes between these in case of
            # jump/switch/yield instructions
            
            for jump_target in basic_block.jump_targets_for_anchor:
                jump_target_block = start_to_basic_block[jump_target]
                if jump_target_block not in basic_block.child_nodes:
                    basic_block.child_nodes.append(jump_target_block)
                if basic_block not in jump_target_block.parent_nodes:
                    jump_target_block.parent_nodes.append(basic_block)
    
        # Link graphes between these when error
        # handling is present
            
        for error_handler in error_handlers:
            if ((basic_block.start_address <= error_handler.start < basic_block.end_address) or
                (basic_block.start_address < error_handler.end <= basic_block.end_address)):
                
                error_handler_block = start_to_basic_block[error_handler.target]
                
                if error_handler_block not in basic_block.error_handling_child_nodes:
                    basic_block.error_handling_child_nodes.append(error_handler_block)
                if basic_block not in error_handler_block.error_handling_parent_nodes:
                    error_handler_block.error_handling_parent_nodes.append(basic_block)

    # WIP...



