#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Tuple, Dict, Set, Sequence, Union, Optional, Any

from defs import BasicBlock, CodePath, DecompiledFunctionBody, HermesDecompiler

# This file is a WIP... And references towards it should eventually be integrated somewhere

def recursive_make_single_code_path(code_path : CodePath, function : DecompiledFunctionBody,
    basic_block : BasicBlock, seen_error_handlers : Set[BasicBlock]):
    
    child_nodes = basic_block.child_nodes + [handler
        for handler in basic_block.error_handling_child_nodes
        if handler not in seen_error_handlers]
    
    # Avoid visiting error handlers too many times:
    seen_error_handlers = set(seen_error_handlers)
    seen_error_handlers |= set(basic_block.error_handling_child_nodes)
    
    cycling = any(component == basic_block for component in code_path.components)
    
    """
    # Not sure if willuse:
    component = CodePathComponent()
    component.basic_block = basic_block
    code_path.components.append(component)
    """
    
    code_path.components.append(basic_block)
    
    if cycling:
        
        basic_block.may_be_cycling_target = True
        code_path.components[-2].may_be_cycling_anchor = True
        code_path.is_cycling_end = True
    
    elif child_nodes:
        
        for child_node in child_nodes[1:]:
            other_code_path = CodePath()
            other_code_path.components = list(code_path.components)
            function.possible_code_paths.append(other_code_path)
            recursive_make_single_code_path(other_code_path, function, child_node, seen_error_handlers)
        
        recursive_make_single_code_path(code_path, function, child_nodes[0], seen_error_handlers)
        
    else:
        
        code_path.is_return_end = True

def make_code_paths_from_function(function : DecompiledFunctionBody, state : HermesDecompiler) -> CodePath:
    
    entry_basic_block = function.basic_blocks[0]    
    
    code_paths = function.possible_code_paths = []
    
    code_path = CodePath()
    code_path.components = []
    code_paths.append(code_path)
    
    recursive_make_single_code_path(code_path, function, entry_basic_block, set())
    
    # WIP ..
    
    
