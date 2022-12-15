#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Tuple, Dict, Set, Sequence, Union, Optional, Any

from defs import HermesDecompiler, DecompiledFunctionBody, BasicBlock

def fill_basic_blocks_into_function(function : DecompiledFunctionBody, state : HermesDecompiler):
    
    asm = function.addr_to_instruction
    
    error_handlers = (state.hbc_reader.function_id_to_exc_handlers[function.function_id]
        if function.function_object.hasExceptionHandler else [])
    
    basic_block_boundaries = ({0} |
        function.try_starts.keys() | function.try_ends.keys() | function.catch_targets.keys() |
        function.jump_anchors.keys() | function.ret_anchors.keys() | function.throw_anchors.keys() |
        function.jump_targets)
    
    basic_blocks = function.basic_blocks = []
    
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
        if basic_block_end in function.ret_anchors:
            may_have_fallen_through = False
            basic_block.anchor_instruction = function.ret_anchors[basic_block_end]
            basic_block.is_unconditional_return_end = True
        elif basic_block_end in function.throw_anchors:
            may_have_fallen_through = False
            basic_block.anchor_instruction = function.throw_anchors[basic_block_end]
            basic_block.is_unconditional_throw_anchor = True
        elif basic_block_end in function.jump_anchors:
            op = function.jump_anchors[basic_block_end]
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
