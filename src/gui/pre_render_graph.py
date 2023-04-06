#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import Dict, List, Set, Tuple, Any, Optional, Sequence
from os.path import dirname, realpath
from collections import defaultdict
from textwrap import fill
from sys import path

GUI_DIR = realpath(dirname(__file__))
SRC_DIR = realpath(GUI_DIR + '/..')
DECOMPILATION_DIR = realpath(SRC_DIR + '/decompilation')
PARSERS_DIR = realpath(SRC_DIR + '/parsers')

path.insert(0, DECOMPILATION_DIR)

from defs import DecompiledFunctionBody, BasicBlock

path.insert(0, PARSERS_DIR)

from hbc_bytecode_parser import ParsedInstruction

TILE_WIDTH_PIXELS = 12
TILE_HEIGHT_PIXELS = 12

BLOCK_WIDTH_CHAR = 80

GRAPH_NODE_WIDTH_TILES = BLOCK_WIDTH_CHAR + 8
GRAPH_NODE_INTERSPACE_HEIGHT_TILES = 5

"""
    TODO: First step: Draw blocks onto the HTML page with position: absolute
    onto a theoritical grid without doing actual graph rendering, then
    add the calculation code?
"""

def draw_stuff(instructions : List[ParsedInstruction], dehydrated : DecompiledFunctionBody) -> dict:

    # Keep track of the vertical space taken in each vertical
    # column as it grows.
    column_index_to_vertical_tile_height : Dict[int, int] = {}

    column_index_to_right_lattice_tiles_2d_array : Dict[int, List[bool]] = defaultdict(list)

    result = {
        'type': 'analyzed_function',
        'function_id': dehydrated.function_id,
        'blocks': []
    } # TODO Defined the layout of this JSON object that should eventually be sent back to the Websocket server

    current_block_text = ''

    y_pos = 5

    for basic_block in dehydrated.basic_blocks:

        # TODO: Use dehydrated.instruction_boundaries here
        start_idx = dehydrated.instruction_boundaries.index(basic_block.start_address)
        end_idx = dehydrated.instruction_boundaries.index(basic_block.end_address)

        current_block_text = ''

        for instruction in instructions[start_idx:end_idx]:

            current_block_text += fill(repr(instruction), BLOCK_WIDTH_CHAR) + '\n'

            pos = instruction.original_pos
            next_pos = instruction.next_pos

            assert (basic_block.start_address <= pos < basic_block.end_address)

            # TODO Set up history API on the web UI too?

        # Output the current block and select the new block:

        num_lines = len(current_block_text.split('\n'))

        block_height = num_lines + 5

        result['blocks'].append({
            'x': 5,
            'y': y_pos,
            'height': block_height,
            'width': GRAPH_NODE_WIDTH_TILES,
            'raw_text': current_block_text,
            'links': ['WIP...']
        })

        y_pos += block_height + GRAPH_NODE_INTERSPACE_HEIGHT_TILES

            
    return result

    # WIP ..