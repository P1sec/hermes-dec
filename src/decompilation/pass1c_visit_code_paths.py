#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Tuple, Dict, Set, Sequence, Union, Optional, Any
from os.path import dirname, realpath
from collections import defaultdict

from defs import HermesDecompiler, BasicBlock, DecompiledFunctionBody
from hbc_bytecode_parser import parse_hbc_bytecode


PER_BLOCK_PIXELS = 12 * 5
PER_INSN_PIXELS = 12

def pass1c_visit_code_paths(state : HermesDecompiler, function_body : DecompiledFunctionBody):

    """
        Use a recursive algorithm to visit the basic blocks tree in
        order to:
        - Mark cycling points of the code
        
        - Calculate the "max_acc_insn_weight" and "max_acc_pixel_weight"
          values (see defs.py) for each basic block
    
        Algorithm:
        - Apply descending recursion starting from the root node of
          the graph (basic block with start instruction pointer 0).

        - In order to avoid recursion loops while iterating (and to
          mark cycling points so that we can identify code loops
          later), keep in a variable passed through recursion a list
          of the basic blocks that have already been recursed through
          for a given code path, also set the "may_be_cycling_anchor"
          and "may_be_cycling_target" flags for BasicBlocks's where
          relevant

          See the previous draft code:
          https://github.com/P1sec/hermes-dec/blob/experimental-control-flow-graph-decompilation/decompilation/graph_traversers/step2_visit_code_paths.py
          https://github.com/P1sec/hermes-dec/blob/experimental-control-flow-graph-decompilation/decompilation/defs.py
    """

    if function_body.basic_blocks:
        desc_recurse_set_cycling_and_accs(function_body.basic_blocks[0], [])

def desc_recurse_set_cycling_and_accs(block : BasicBlock, code_path : List[BasicBlock]):

    child_nodes = block.child_nodes + block.error_handling_child_nodes

    cycling = block in code_path
    
    if cycling:
        block.may_be_cycling_target = True
        code_path[-1].may_be_cycling_anchor = True
        return
    
    if code_path:
        
        acc_insn_weight = code_path.max_acc_insn_weight[-1]
        acc_insn_weight += block.insn_count

        block.max_acc_insn_weight = max(block.max_acc_insn_weight, acc_insn_weight)

        acc_pixel_weight = code_path.max_acc_pixel_weight[-1]
        acc_pixel_weight += PER_BLOCK_PIXELS + block.insn_count * PER_INSN_PIXELS

        block.max_acc_pixel_weight = max(block.max_acc_pixel_weight, acc_pixel_weight)
    
    code_path.components.append(block)

    for child_node in child_nodes:
        desc_recurse_set_cycling_and_accs(child_node, list(code_path))

