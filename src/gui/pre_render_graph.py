#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import Dict, List, Set, Tuple, Any, Optional, Sequence
from os.path import dirname, realpath
from collections import defaultdict
from sys import path

GUI_DIR = realpath(dirname(__file__))
SRC_DIR = realpath(GUI_DIR + '/..')
DECOMPILATION_DIR = realpath(SRC_DIR + '/decompilation')
PARSERS_DIR = realpath(SRC_DIR + '/parsers')

path.insert(0, DECOMPILATION_DIR)

from defs import DecompiledFunctionBody, BasicBlock

path.insert(0, PARSERS_DIR)

from hbc_bytecode_parser import ParsedInstruction


def draw_stuff(instructions : List[ParsedInstruction], dehydrated : DecompiledFunctionBody) -> dict:

    current_x = 1 # The horizontal alighments of the basic blocks in the CSS grid layout should approximately
        # match the indent levels in the future decompiled code for now. 
    current_y = 1 # One basic block per row will be rendered in the CSS grid layout for now.

    result = {
        'type': 'analyzed_function',
        'function_id': dehydrated.function_id,
        'blocks': []
    } # TODO Defined the layout of this JSON object that should eventually be sent back to the Websocket server

    def process_basic_block(basic_block : BasicBlock):

        nonlocal current_x
        nonlocal current_y

        if basic_block.rendered:
            return
        basic_block.rendered = True

        start_idx = dehydrated.instruction_boundaries.index(basic_block.start_address)
        end_idx = dehydrated.instruction_boundaries.index(basic_block.end_address)

        current_block_text = ''

        for instruction in instructions[start_idx:end_idx]:

            current_block_text += repr(instruction) + '\n'

            # pos = instruction.original_pos
            # next_pos = instruction.next_pos

            # assert (basic_block.start_address <= pos < basic_block.end_address)

            # TODO Set up history API on the web UI too?

        # Output the current block and select the new block:

        result['blocks'].append({
            'grid_x': current_x,
            'grid_y': current_y,
            'text': current_block_text,
            'links': ['WIP...']
        })

        # Recursively iterate through children blocks:

        child_nodes = sorted(basic_block.child_nodes + basic_block.error_handling_child_nodes,
            key = lambda block: (-block.max_acc_insn_weight, block.start_address))

        child_nodes = list(filter(lambda block: (not block.rendered) and (not block.marked_to_render),
            child_nodes))
        
        for child_node in child_nodes:
            child_node.marked_to_render = True

        orig_x = current_x
        for x_offset, child_node in reversed(list(enumerate(child_nodes))):
            current_y += 1

            current_x = orig_x + x_offset
            process_basic_block(child_node)

    if dehydrated.basic_blocks:
        process_basic_block(dehydrated.basic_blocks[0])

            
    return result

    # WIP ..