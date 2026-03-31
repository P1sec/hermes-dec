This file contains detailed write-up of the thoughts
produced while drafting the algorithm present in the
`src/decompilation/pass1c_visit_code_paths.py` code file (the
current algorithm is simpler than this).

## Documentation of sub-algorithm 1 (draft -1)

    In sub-algo 1:
    
    At a given moment, a visitable node may either be
    tip-of-branch or not tip-of-branch (branch = code exploration path).
    
    At a given moment, the tip-of-branches are stored in the
    global state of the algorithm (through the fact that
    the branches are stored in the "alg_state.branches"
    list)
    
    The only initial branch is just composed of the root node of the tree.
    
    Branches fork when, a child has been linked (found/marked as
    a visited child) in a tip-of-branch node, but other non-visited
    children remain.
    
    Branches merge when, after any update of the ongoing branches,
    the same node has gotten to be the end of two branches.
     => This is done so that the new algorithm is *way* less greedy
        than the former one.
    
    Branches end when, all the children of a given tip-of-branch
    have been marked visited. They are then suppressed from "alg_state.branches".
    
    Child nodes are marked cycling during the update process of a
    branch (simple update or consequential merge), when they
    already been seen in a given branch.
    
    The sub-algorithm 1 ends when, all branches have ended in
    the global state ("alg_state.branches" is empty).


-----------------

## Documentation of the `VisitableNode.match_against_child` function (draft -1)


    This function is called by the main routine of
    sub-algorithm 1 when the current node has been
    pre-identified as a potentiel child of any of
    the current tip-of-branch nodes (see the definition above)
    and pre-sorted so that we visit nodes upper in
    the global basic blocks tree first, and that we
    maintain less code exploration paths/branches in
    memory in parallel, and that our algorithm is more
    BFS than DFS and hence shorter to execute in the
    use case of sub-algorithm 1 overall.
    
    It should first check whether the passed other node
    of the tree is actually part of the unvisited
    children of the present tip-of-branch node.
    
    If this is the case,
    - We should mark the concerned child as visited
      in our local state
    - We should check whether all the children of the
      current object are now considered visited in
      our local state, and act upon it:
      (This should be performed by "alg_state.do_needed_fork_and_merge_ops")
      - In not, we should do fork action
        (are there still unvisited nodes present within
         the local state for the current object right now?)
      - We should change the tip-of-branch the current
        node is part of (leaving a forked copy if there
        are still unvisited child nodes referenced in
        the local state for the current node)

        [tricky - please clarify]
      - We should check for necessity of merge action
        (comparing all the branch present in the
         "alg_state.branches" array and checking
          whether, with the new tip-of-branches in
          presence, there are now code paths to be
          merged together)
      - We should perform the merge if this is the
        case, retaining nodes
        [/tricky - please clarify]
    
    - We should check for potential cycling across
      the branches having the checked over child
      as their (new) tip, after the fork and
      merge operations described above have been
      conducted
    - We should perform a partial burn action if there
      is indeed cycling
       - And check for the necessity of fork-and-merge
         action again
        (call "alg_state.do_needed_fork_and_merge_ops" again)
    - We should perform the delete branch action if the
      new tip-of-branch has no child
    
    def match_against_child(self, other_node):


-------------------------


# Tentative sub-algorithm 1 (only to detect and list cycling points) - draft -2

(explained more in the comments about the "VisitableNode"
class definition below)

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
