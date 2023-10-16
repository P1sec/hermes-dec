#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Tuple, Dict, Set, Sequence, Union, Optional, Any
from os.path import dirname, realpath
from collections import defaultdict

from defs import HermesDecompiler, BasicBlock, DecompiledFunctionBody
from hbc_bytecode_parser import parse_hbc_bytecode

"""
    Please see the "docs/Pass1c Cycling detection + Block Distance from root
    Weighting Algo.md" file for documentation regarding the functioning of the
    algorithms present in the current file.
"""


PER_BLOCK_PIXELS = 12 * 5
PER_INSN_PIXELS = 12

class CycleDetectorAlgState:

    all_nodes : List['VisitableNode']

    # State of sub-algo 1:
    branches : List['CodeExplorationPath'] # Contains references to parents with fork points

    function_body : DecompiledFunctionBody

    def __init__(self, function_body : DecompiledFunctionBody):
        self.function_body = function_body
        self.all_nodes = []
        self.branches = []

    def do_initial_linking(self):
        for node in self.all_nodes:
            node.do_initial_linking()

# Pass1c algorithm calculation steps:
#   - Sub-algo 1: detect cycling points in the graph.
#   - Sub-algo 2: iterate over the graph BFS,
#     accumulating instruction weights just stopping
#     at the cycle points.

class VisitableNode:

    alg_state : CycleDetectorAlgState

    wrapped : ['BasicBlock']

    unvisited_children : Set['VisitableNode']
    visited_children : Set['VisitableNode']

    cycling_visited_children : Set['VisitableNode']

    # The present object may only be the tip of
    # one branch at the time
    current_tip_of : Optional['CodeExplorationPath']

    # part_of_code_paths : Set['CodeExplorationPath']

    # Comment for now: Will only be useful in sub-algo 2
    # temp_max_insn_acc : int

    def __init__(self, node, alg_state):
        self.wrapped = node
        self.current_tip_of = None
        self.cycling_visited_children = set()
        # self.part_of_code_paths = set()
        self.visited_children = set()
        self.alg_state = alg_state
        self.alg_state.all_nodes.append(self)
    
    def do_initial_linking(self):
        self.unvisited_children = set(
            self.alg_state.all_nodes[
                self.alg_state.function_body.basic_blocks.index(unwrapped_item)]
            for unwrapped_item in self.wrapped.child_nodes + self.wrapped.error_handling_child_nodes
        )

    # See the "docs/Pass1c Cycling detection + Block Distance
    # from root Weighting Algo.md" documentation for a detailed
    # description of the algorithm departing from this function

    def match_against_child(self, other_node):
        assert other_node in self.unvisited_children

        self.unvisited_children.discard(other_node)
        self.visited_children.add(other_node)

        assert self.current_tip_of

        # Do a forking merge op:
        if self.unvisited_children and other_node.current_tip_of:
            other_node.current_tip_of.copy_merge(self.current_tip_of)
        # Do a non-forking merge op:
        elif other_node.current_tip_of:
            other_node.current_tip_of.copy_merge(self.current_tip_of)
            self.current_tip_of.prune_self()
        # Do a fork with modified tip op:
        elif self.unvisited_children:
            self.current_tip_of.fork_with_new_tip(other_node)
        # Do a change tip op:
        else:
            self.current_tip_of.append_tip(other_node)

        # Do pruning if now cycling (and mark as cycling)
        will_create_cycle = other_node in other_node.current_tip_of.children[:-1]

        if will_create_cycle:
            self.cycling_visited_children.add(other_node)
            self.wrapped.may_be_cycling_anchor = True
            other_node.wrapped.may_be_cycling_target = True

            other_node.current_tip_of.prune_self()
        
        # Do pruning in all cases
        if other_node.current_tip_of and not other_node.unvisited_children:
            other_node.current_tip_of.prune_self()
        
        if self.current_tip_of and not self.unvisited_children:
            self.current_tip_of.prune_self()

    # Props (i/o) to be used from the BasicBlocks object:

    # max_acc_insn_weight : int <-- output of sub-alg 2

    # may_be_cycling_anchor : bool <-- output of sub-alg 1
    # may_be_cycling_target : bool <-- output of sub-alg 1

    # child_nodes : List['BasicBlock'] <-- input
    # parent_nodes : List['BasicBlock'] <-- input

    # error_handling_child_nodes : List['BasicBlock'] <-- input
    # error_handling_parent_nodes : List['BasicBlock'] <-- input

    # ^ Use Sets or Lists?

class CodeExplorationPath:

    children : List[VisitableNode]

    alg_state : CycleDetectorAlgState

    def __init__(self, children, alg_state):

        self.children = children
        self.alg_state = alg_state
        self.alg_state.branches.append(self)

        assert not children[-1].current_tip_of
        children[-1].current_tip_of = self
    
    def copy_merge(self, other_branch : 'Self'):
        non_common_descents = [
            node for node in self.children
            if node not in other_branch.children
        ]

        other_branch.children = (other_branch.children[:-1] +
            non_common_descents + # Right?
            other_branch.children[-1:])
    
    def prune_self(self):
        assert self.children[-1].current_tip_of == self

        self.children[-1].current_tip_of = None
        self.alg_state.branches.remove(self)
    
    def fork_with_new_tip(self, other_node : VisitableNode):
        assert self.children[-1].current_tip_of == self
        assert not other_node.current_tip_of
        
        CodeExplorationPath(self.children + [other_node], self.alg_state)
    
    def append_tip(self, other_node : VisitableNode):
        assert self.children[-1].current_tip_of == self
        assert not other_node.current_tip_of
        
        self.children[-1].current_tip_of = None
        self.children.append(other_node)
        other_node.current_tip_of = self

def pass1c_visit_code_paths(state : HermesDecompiler, function_body : DecompiledFunctionBody):

    """
        Use a recursive algorithm to visit the basic blocks tree in
        order to:
        - Sub-algorithm 1: Mark cycling points of the code
            - Useful for detecting loops in the control flow-enabled decompilation
              process later
        
        - Sub-algorithm 2 (TODO): Calculate the "max_acc_insn_weight" value (see
            defs.py) for each basic block
            - Useful for visually sorting the order of blocks in the
              web UI graph
            - Useful for detecting condition definition priority in the
              control flow-enabled decompilation process later
    
    """

    all_nodes = function_body.basic_blocks
    root_node = all_nodes[0]

    # Check whether there is no backward jump into the
    # basic block graphes: in this case, there is no
    # loop and hence no cycling point/no need to process
    # further the decompiled function

    cycles = False
    for node in all_nodes:
        node_index = all_nodes.index(node)
        for other_node in node.child_nodes + node.error_handling_child_nodes:
            if all_nodes.index(other_node) < node_index:
                cycles = True
                break
        if cycles:
            break
    if not cycles:
        return

    # Build up state and create an initial exploration path
    # containing the root node of the function basic blocks
    # graph

    root_node.max_acc_insn_weight = root_node.insn_count

    state = CycleDetectorAlgState(function_body)

    for node in all_nodes:
        VisitableNode(node, state) # <- state.all_nodes
    CodeExplorationPath([state.all_nodes[0]], state) # <- state.branches

    state.do_initial_linking()

    while state.branches:

        nodes_to_explore = set()
        for branch in state.branches:
            nodes_to_explore |= branch.children[-1].unvisited_children

        assert nodes_to_explore

        nodes_to_explore = sorted(
            nodes_to_explore,
            key = lambda block: (
                # TODO: Opti this
                # len(block.wrapped.parent_nodes) +
                #     len(block.wrapped.error_handling_parent_nodes),
                block.wrapped.start_address
            )
        )

        next_node = nodes_to_explore.pop(0)

        for branch in state.branches:
            if next_node in branch.children[-1].unvisited_children:
                branch.children[-1].match_against_child(next_node)
                break

