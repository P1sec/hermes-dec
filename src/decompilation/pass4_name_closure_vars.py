#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Tuple, Dict, Set, Sequence, Union, Optional, Any
from sys import stderr

from defs import HermesDecompiler, DecompiledFunctionBody, Environment, TokenString, ForInLoopInit, ForInLoopNextIter, RawToken, ReturnDirective, ThrowDirective, JumpNotCondition, JumpCondition, AssignmentToken, BasicBlock, LeftParenthesisToken, RightHandRegToken,  RightParenthesisToken, LeftHandRegToken, NewEnvironmentToken, StoreToEnvironment, GetEnvironmentToken, LoadFromEnvironmentToken, FunctionTableIndex

# Implementation for the "NameNonLocalClosureVariables" algorithm (see the .odt notes)

"""
    NOTES about the original Hermes `lib/VM/Interpreter.cpp` file
    handling instructions such as `GetEnvironment`, `CreateEnvironment`,
    `StoreToEnvironment`, `LoadFromEnvironment`:
        - "FRAME.getCalleeClosureUnsafe()->getEnvironment(runtime)"
            ^ This seems to fetch the operand 2 of Call* calls
            containing a closure reference for the current function
        - "curEnv->getParentEnvironment(runtime)"
            ^ This fetches the environement that was to the current
            function's passed-environment at the point of creating
            `curEnv` (through indirecting a linked list), or likely
            the caller's environment
"""

def pass4_name_closure_vars(state : HermesDecompiler, function_body : DecompiledFunctionBody):

    AT = AssignmentToken

    TS = TokenString
    RT = RawToken
    LHRT = LeftHandRegToken
    RHRT = RightHandRegToken

    function_body.local_items : Dict[int, Environment] = {}
    
    parent_environment = function_body.parent_environment

    lines = function_body.statements
    for index, line in enumerate(lines):
        for token in line.tokens:

            if isinstance(token, NewEnvironmentToken):
            
                function_body.local_items[token.register] = Environment(parent_environment, (parent_environment.nesting_quantity + 1) if parent_environment else 0, {})
                line.tokens = [] # Silence this instruction in the produced decompiled code
                
            elif isinstance(token, GetEnvironmentToken):

                environment = parent_environment
                for nesting in range(token.nesting_level):
                    environment = environment.parent_environment
                
                function_body.local_items[token.register] = environment
                line.tokens = [] # Silence this instruction in the produced decompiled code
    
            elif isinstance(token, FunctionTableIndex):

                if token.environment_id is not None:
                    token.parent_environment = function_body.local_items[token.environment_id]

            elif isinstance(token, StoreToEnvironment):
                varname = '_closure%d_slot%d' % (function_body.local_items[token.env_register].nesting_quantity,
                    token.slot_index)
                
                if token.slot_index not in function_body.local_items[token.env_register].slot_index_to_varname:
                    function_body.local_items[token.env_register].slot_index_to_varname[token.slot_index] = varname
                    line.tokens = [RT('var ' + varname), AT(), RHRT(token.value_register)]
                
                else: # This a closure-referenced variable reassignment
                    line.tokens = [RT(varname), AT(), RHRT(token.value_register)]
                
            elif isinstance(token, LoadFromEnvironmentToken):
                var_name = '_closure%d_slot%d' % (function_body.local_items[token.register].nesting_quantity,
                    token.slot_index)
                
                line.tokens[2] = RT(var_name)
    