#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Tuple, Dict, Set, Sequence, Union, Optional, Any
from os.path import dirname, realpath
from dataclasses import dataclass

from defs import HermesDecompiler, DecompiledFunctionBody, TokenString, ForInLoopInit, ForInLoopNextIter, RawToken, ReturnDirective, ThrowDirective, JumpNotCondition, JumpCondition, AssignmentToken, BasicBlock, LeftParenthesisToken, RightHandRegToken,  RightParenthesisToken, LeftHandRegToken, NewEnvironmentToken, StoreToEnvironment, GetEnvironmentToken, LoadFromEnvironmentToken, FunctionTableIndex

class Pass3StructureDecompiledFlow:
    
    def __init__(self, state : HermesDecompiler):

        JNC = JumpNotCondition # Forward jumps
        JC = JumpCondition # Backwards jumps

        RD = ReturnDirective
        TD = ThrowDirective

        AT = AssignmentToken

        TS = TokenString
        RT = RawToken
        LHRT = LeftHandRegToken
        RHRT = RightHandRegToken

        FILI = ForInLoopInit
        FILNI = ForInLoopNextIter

        LPT = LeftParenthesisToken
        RPT = RightParenthesisToken
        
        # a) Implementation for recreating "for..in" structures (see the .odt notes)
        
        for function_count, function_header in enumerate(state.hbc_reader.function_headers):
            
            function_body = state.function_id_to_body[function_count]
            lines = function_body.statements
            
            for index, line in enumerate(lines):
                # Seek for a GetPNameList instruction
                has_fili = line.tokens and isinstance(line.tokens[0], FILI)
                
                if has_fili:
                    
                    # Seek for a GetNextPName instruction further it
                    other_index = next((other_index
                        for other_index in range(index, len(lines))
                        if isinstance(lines[other_index].tokens[0], FILNI)), None)
                    assert other_index
                    
                    # print('DDD', lines[index:index + 6], ' ? /// ', lines[other_index:other_index + 6])
                    
                    # The beginning point of the loop's inner basic block
                    # will be:
                    begin_address = lines[index + 2].assembly[0].original_pos
                    
                    if (isinstance(lines[index + 1].tokens[0], JC) and
                        isinstance(lines[other_index + 1].tokens[0], JC)):
                        
                        # There is a nested loop and we're going to an
                        # instruction located backwards in the HBC after
                        # the end of the current for..in loop (hence the JC
                        # rather than JNC token in our intermediate
                        # representation), manage to find the end of the
                        # current basic block through iterating over code
                        
                        for further_index in range(other_index + 2, len(lines)):
                            
                            if (isinstance(lines[further_index].tokens[0], JC) and
                                lines[further_index].tokens[0].target_address == begin_address and
                                lines[further_index].tokens[1] == RT('true')):
                                
                                # We've found an unconditional backwards jump towards
                                # the beginning of the loop, close the current basic
                                # block
                                break
                            
                            if (isinstance(lines[further_index].tokens[0], RD) or
                                isinstance(lines[further_index].tokens[0], TD)):
                                
                                # We've found either a "return" or a "throw"
                                # instruction, likely located after a conditional
                                # jump towards the beginning of the current basic
                                # block, close the current basic block
                                break
                        
                        end_address = lines[further_index + 1].assembly[0].original_pos
                    
                    else:
                        
                        # There is no nested loop and we're having the end
                        # address of the current loop located directly in
                        # the first conditional jump located after the
                        # respective GetPNameList and GetNextPName
                        # instructions within the original HBC
                        
                        end_address = lines[other_index + 1].tokens[0].target_address
                    
                        assert isinstance(lines[index + 1].tokens[0], JNC)
                        assert isinstance(lines[other_index + 1].tokens[0], JNC)
                        
                        boundary_1 = lines[index + 1].tokens[0].target_address
                        boundary_2 = lines[other_index + 1].tokens[0].target_address
                        
                        min_boundary = min(boundary_1, boundary_2)
                        max_boundary = max(boundary_1, boundary_2)
                        if min_boundary != max_boundary:
                            for further_index in range(other_index + 2, len(lines)):    
                                if min_boundary <= lines[further_index].assembly[0].original_pos < max_boundary:
                                    lines[further_index].tokens.insert(0, RT('// NOTE: Orphan basic block present beween two condition branches automatically created upon For..in loop: '))
                    
                    #print('EEEEE ([. DEBUG]', lines[index], ':///', lines[index + 1], '/D/D+', lines[other_index], '/D+D+D', lines[other_index + 1])
                    
                    line.tokens = [RT('for'), LPT(), LHRT(lines[other_index].tokens[0].next_value_register),
                     RT(' in '), RHRT(line.tokens[0].obj_register), RPT()]
                    lines[index + 1].tokens = []
                    lines[other_index].tokens = []
                    lines[other_index + 1].tokens = []
                    
                    continue
        
        # b) Implementation for the "NameNonLocalClosureVariables" algorithm (see the .odt notes)
        
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
        
        @dataclass
        class Environment:
            parent_environment : Optional['Environment']
            nesting_quantity : int
            slot_index_to_varname : Dict[int, str]
        
        def recursively_name_non_locale_closure_variables(function_body : DecompiledFunctionBody, parent_environment : Optional[Environment]):
            local_items : Dict[int, VariableStackItems] = {} # {env_register: Environment}
            
            lines = function_body.statements
            for index, line in enumerate(lines):
                for token in line.tokens:
                    if isinstance(token, NewEnvironmentToken):
                        local_items[token.register] = Environment(parent_environment, (parent_environment.nesting_quantity + 1) if parent_environment else 0, {})
                        line.tokens = [] # Silence this instruction in the produced decompiled code
                    elif isinstance(token, StoreToEnvironment):
                        varname = '_closure%d_slot%d' % (local_items[token.env_register].nesting_quantity,
                            token.slot_index)
                        if token.slot_index not in local_items[token.env_register].slot_index_to_varname:
                            local_items[token.env_register].slot_index_to_varname[token.slot_index] = varname
                            line.tokens = [RT('var ' + varname), AT(), RHRT(token.value_register)]
                        else: # This a closure-reference variable reassignment
                            line.tokens = [RT(varname), AT(), RHRT(token.value_register)]
                    elif isinstance(token, GetEnvironmentToken):
                        environment = parent_environment
                        for nesting in range(token.nesting_level):
                            environment = environment.parent_environment
                        local_items[token.register] = environment
                        line.tokens = [] # Silence this instruction in the produced decompiled code
                    elif isinstance(token, FunctionTableIndex):
                        if ((token.is_closure or token.is_generator) and
                            token.environment_id is not None):
                            recursively_name_non_locale_closure_variables(
                                state.function_id_to_body[token.function_id],
                                local_items[token.environment_id])
                                        # WIP)
                        # Don't touch closure calls
                    elif isinstance(token, LoadFromEnvironmentToken):
                        var_name = '_closure%d_slot%d' % (local_items[token.register].nesting_quantity,
                            token.slot_index)
                        line.tokens[2] = RT(var_name)
            
            # WIP ..
        
        global_function = state.function_id_to_body[state.hbc_reader.header.globalCodeIndex]
        
        recursively_name_non_locale_closure_variables(global_function, None)
    
