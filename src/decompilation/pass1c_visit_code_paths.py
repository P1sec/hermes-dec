#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Tuple, Dict, Set, Sequence, Union, Optional, Any
from os.path import dirname, realpath
from collections import defaultdict

from defs import HermesDecompiler, BasicBlock, DecompiledFunctionBody
from hbc_bytecode_parser import parse_hbc_bytecode


PER_BLOCK_PIXELS = 12 * 5
PER_INSN_PIXELS = 12

class CycleDetectorAlgState:

    all_nodes : List['VisitableNode']

    # State of sub-algo 1:
    branches : List['CodeExplorationPath'] # Contains references to parents with fork points

    def __init__(self, visitable_nodes):
        self.branches = []

    def do_needed_fork_and_merge_ops(self):
        xx_wip

# Pass1c algorithm calculation steps:
#   - Sub-algo 1: detect cycling points in the graph.
#   - Sub-algo 2: iterate over the graph BFS,
#     accumulating instruction weights just stopping
#     at the cycle points.

class VisitableNode:

    # In sub-algo 1:
    #
    # At a given moment, a visitable node may either be
    # tip-of-branch or not tip-of-branch (branch = code exploration path).
    #
    # At a given moment, the tip-of-branches are stored in the
    # global state of the algorithm (through the fact that
    # the branches are stored in the "alg_state.branches"
    # list)
    #
    # The only initial branch is just composed of the root node of the tree.
    #
    # Branches fork when, a child has been linked (found/marked as
    # a visited child) in a tip-of-branch node, but other non-visited
    # children remain.
    #
    # Branches merge when, after any update of the ongoing branches,
    # the same node has gotten to be the end of two branches.
    #  => This is done so that the new algorithm is *way* less greedy
    #     than the former one.
    #
    # Branches end when, all the children of a given tip-of-branch
    # have been marked visited. They are then suppressed from "alg_state.branches".
    #
    # Child nodes are marked cycling during the update process of a
    # branch (simple update or consequential merge), when they
    # already been seen in a given branch.
    #
    # The sub-algorithm 1 ends when, all branches have ended in
    # the global state ("alg_state.branches" is empty).

    alg_state : CycleDetectorAlgState

    underlying_node : [BasicBlock]

    unvisited_children : Set[BasicBlock]
    visited_children : Set[BasicBlock]

    cycling_visited_children : Set[BasicBlock]

    part_of_code_paths : ['CodeExplorationPath']

    # Comment for now: Will only be useful in sub-algo 2
    # temp_max_insn_acc : int

    def __init__(self, node, parent_path, alg_state):
        self.underlying_node = node
        self.unvisited_children = set(node.child_nodes + node.error_handling_child_nodes)
        self.part_of_code_paths = defaultdict(set)
        self.alg_state = alg_state

    # This function is called by the main routine of
    # sub-algorithm 1 when the current node has been
    # pre-identified as a potentiel child of any of
    # the current tip-of-branch nodes (see the definition above)
    # and pre-sorted so that we visit nodes upper in
    # the global basic blocks tree first, and that we
    # maintain less code exploration paths/branches in
    # memory in parallel, and that our algorithm is more
    # BFS than DFS and hence shorter to execute in the
    # use case of sub-algorithm 1 overall.
    #
    # It should first check whether the passed other node
    # of the tree is actually part of the unvisited
    # children of the present tip-of-branch node.
    #
    # If this is the case,
    # - We should mark the concerned child as visited
    #   in our local state
    # - We should check whether all the children of the
    #   current object are now considered visited in
    #   our local state, and act upon it:
    #   (This should be performed by "alg_state.do_needed_fork_and_merge_ops")
    #   - We should check for necessity of fork action
    #     (are there still unvisited nodes present within
    #      the local state for the current object right now?)
    #   - We should change the tip-of-branch the current
    #     node is part of (leaving a forked copy if there
    #     are still unvisited child nodes referenced in
    #     the local state for the current node)
    #   - We should check for necessity of merge action
    #     (comparing all the branch present in the
    #      "alg_state.branches" array and checking
    #       whether, with the new tip-of-branches in
    #       presence, there are now code paths to be
    #       merged together)
    #   - We should perform the merge if this is the
    #     case, retaining nodes
    # - We should check for potential cycling across
    #   the branches having the checked over child
    #   as their (new) tip, after the fork and
    #   merge operations described above have been
    #   conducted
    # - We should perform a partial burn action if there
    #   is indeed cycling
    #    - And check for the necessity of fork-and-merge
    #      action again
    #     (call "alg_state.do_needed_fork_and_merge_ops" again)
    # - We should perform the delete branch action if the
    #   new tip-of-branch has no child
    #
    def match_against_children(self, other_node):
        if other_node in self.unvisited_children:
            self.unvisited_children.discard(other_node)
            self.visited_children.add(other_node)

            self.do_needed_fork_and_merge_ops()
            if self.do_cycling_and_burn_check_ops(self):
                self.do_needed_fork_and_merge_ops()
            self.do_prune_if_no_tip_of_branch()

    def do_needed_fork_and_merge_ops(self):
        self.alg_state.do_needed_fork_and_merge_ops()
    
    # Returns True if any partial burn operation (as
    # described in the top comment of the class) has
    # been performed
    def do_cycling_and_burn_check_ops(self, other_node) -> bool:
        if xx:
            self.set_cycling_pair(other_node)
            xx
    
    def set_cycling_pair(self, other_node):
        self.cycling_visited_children.add(other_node)
        self.node.may_be_cycling_anchor = True
        other_node.may_be_cycling_target = True
    
    def partial_burn_op(self):
        xx
    
    def do_prune_if_no_tip_of_branch(self):
        xx

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

    children : List[BasicBlock]

    def __init__(self, initial_node):

        self.children = [initial_node]

def pass1c_visit_code_paths(state : HermesDecompiler, function_body : DecompiledFunctionBody):

    """
        Use a recursive algorithm to visit the basic blocks tree in
        order to:
        - Sub-algorithm 1: Mark cycling points of the code
            - Useful for detecting loops in the control flow-enabled decompilation
              process later
        
        - Sub-algorithm 2: Calculate the "max_acc_insn_weight" value (see
            defs.py) for each basic block
            - Useful for visually sorting the order of blocks in the
              web UI graph
            - Useful for detecting condition definition priority in the
              control flow-enabled decompilation process later
    
    """

    """
        WIP sub-algorithm 1 (only to detect and list cycling points):
        (explained more in the comments about the "VisitableNode"
        class definition below)

        <NEW MAKET>
            (Pre-step but seldom useful: If there is no backward jump
            in the subroutine, there is no cycling, exit the current algorithm)

            Define a list of exploration paths, with the initial exploration
            path only containing the root of the graph.

            We'll do a kind of weighted BFS-alike algorithm with a queue
            of vertices (nodes) that we will,
                a. at each iteration, process with
                    aa. filtering temporarily only which have a parent
                        in an existing exploration path AND had not
                        all their childs? parents? both? visited
                    ab. (and keeping these sorted upon origin position in
                         the code)
                    ac. Obviously process the nodes that have only one
                        extra parent to be visited first!
                    ad. (Put point which have been determined to cycle
                         the farthest possible in the list?)

                        ^ Likely use a pattern like this

                        sorted(
                            x,
                            (
                                key1,
                                -key2,
                                -key3,
                                key4,
                                key5,
                                ..
                            )
                        )
                    
                    (...)
                    a3. Keep track of the max read instruction path
                        (still in the structure) in the meantime

                    a4x. Whenever we branch to 2+ unvisited nodes in the
                         graph, split exploration paths
                            (Each exploration path having n parents with
                            split points, resembling a bit the principle
                            of Git commit trees)
                    a4y. Whenever a node/edge have had all their inbound
                         paths visited, visit back up to split points
                         and see which exploration paths to merge
                    
                    (...)
                    a4z. Merge cycling points whenever required

            (In the end we'll have a list of the cycling points in the graph
                + possibly imperfect max insn weights calculated everywhere)
        </NEW MAKET>

        <REMINDER>
            Queue = FIFO = Premier entré (mis à la fin de la queue en premier),
                premier dehors (sorti du début de la queue en premier)
            Stack (pile) = LIFO = Dernier entré (mis en haut de la pile en dernier),
                premier dehors (sorti du haut de la pile en premier)
            
            BFS = Breadth-first search = Algo de parcours de graphe par recherche
                sur la largeur en premier = itère horizontalement puis verticalement,
                utilise une queue
            DFS = Depth-first search = Algo de parcours de graphe par recherche
                sur la profondeur en premier = itère verticalement puis horizontalement
                
            Vertice = Sommet = Point/Nœud du graphe
            Edge = Tige = Trait/Lien du graphe

        </REMINDER>
        
    """

    all_nodes = function_body.basic_blocks
    root_node = all_nodes[0]

    all_nodes_set = set(all_nodes)

    root_child_nodes = root_node.child_nodes + root_node.error_handling_child_nodes

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

    state = CycleDetectorAlgState()

    state.visited_nodes.add(root_node)
    state.unvisited_nodes = all_nodes_set - state.visited_nodes

    code_path = CodeExplorationPath()
    code_path.children.append(root_node)

    state.exploration_paths.append(code_path)

    state.next_child_nodes = root_child_nodes

    while state.next_child_nodes:

        state.next_child_nodes = sorted(
            state.next_child_nodes,
            lambda block: (
                block in state.visited_nodes,
                len(block.parent_nodes),
                block.start_address
            )
        )

        next_node = state.next_child_nodes.pop(0)

        state.visited_nodes.add(next_node)
        state.unvisited_nodes.discard(next_node)
        state.next_child_nodes.discard(next_node)

        state.next_child_nodes |= next_node.child_nodes + next_node.error_handling_child_nodes

        # Handle self-cycling nodes
        if next_node in next_node.child_nodes:
            next_node.may_be_cycling_anchor = True
            next_node.may_be_cycling_target = True
        
        # Handle normal cycling path + continuation path
        for exploration_path in state.exploration_paths:
            if next_node in (exploration_path.children[-1].child_nodes +
                exploration_path.children[-1].error_handling_child_nodes):

            if next_node in exploration_path.children:

                exploration_path.children.append(next_node)

                # Handle when all the children in the tip of the
                # currently iterated over node have been visited,
                # leveraging the state.node_to_visited_children property

                state.node_to_visited_children[next_node].add(xx)

                # (..xx Update state.node_to_exploration_paths_included)
                state.node_to_exploration_paths_included[next_node].add(xx)
                xx

                # If other child nodes of the completed item have not been
                # visited yet, perform fork action when needed
                state.node_to_exploration_paths_included[next_node].add(xx)
                xx

        # Handle handling loops by allowing to restack already visited nods

        pass # WIP XX

    


