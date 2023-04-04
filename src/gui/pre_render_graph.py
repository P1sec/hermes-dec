#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import Dict, List, Set, Tuple, Any, Optional, Sequence
from os.path import dirname, realpath
from collections import defaultdict
from textwrap import wrap

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

GRAPH_NODE_WIDTH_TILES = 20
GRAPH_NODE_INTERSPACE_HEIGHT_TILES = 5

"""
    TODO: First step: Draw blocks onto the HTML page with position: absolute
    onto a theoritical grid without doing actual graph rendering, then
    add the calculation code?
"""

def 

def draw_stuff(instructions : List[ParsedInstruction], dehydrated : DecompiledFunctionBody) -> dict:

    # Keep track of the vertical space taken in each vertical
    # column as it grows.
    column_index_to_vertical_tile_height : Dict[int, int] = {}

    column_index_to_right_lattice_tiles_2d_array : Dict[int, List[bool]] = defaultdict(list)

    result = {} # TODO Defined the layout of this JSON object that should eventually be sent back to the Websocket server

    basic_blocks = dehydrated.basic_blocks

    current_block = basic_blocks[0]

    for instruction in instructions:

        pos = instruction.original_pos
        if not (current_block.start_address <= pos < current_block.end_address):

            # Output the current block and select the new block:

            # TODO: WIP (Output the block here with wrapped text etc.)

            current_block = basic_blocks[basic_blocks.index(current_block) + 1]
            assert current_block.start_address <= pos < current_block.end_address
            # WIP ..
    

    return result

    # WIP ..