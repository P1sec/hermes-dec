#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Tuple, Dict, Set, Sequence, Union, Optional, Any
from os.path import dirname, realpath
from dataclasses import dataclass

from defs import HermesDecompiler, DecompiledFunctionBody, Environment, TokenString, ForInLoopInit, ForInLoopNextIter, RawToken, ReturnDirective, ThrowDirective, JumpNotCondition, JumpCondition, AssignmentToken, BasicBlock, LeftParenthesisToken, RightHandRegToken,  RightParenthesisToken, LeftHandRegToken, NewEnvironmentToken, StoreToEnvironment, GetEnvironmentToken, LoadFromEnvironmentToken, FunctionTableIndex

def pass3_parse_forin_loops(state : HermesDecompiler, function_body : DecompiledFunctionBody):

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
    
    # Implementation for recreating "for..in" structures (see the .odt notes)

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
                
                continue # Commented yet: Show not to always work

                """
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
                """
            
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
                    weird_case = False
                    for further_index in range(other_index + 2, len(lines)):    
                        if min_boundary <= lines[further_index].assembly[0].original_pos < max_boundary:
                            weird_case = True
                            # lines[further_index].tokens.insert(0, RT('// NOTE: Orphan basic block present beween two condition branches automatically created upon For..in loop: '))
                            break
                    if weird_case:
                        continue
            
            function_body.basic_blocks.append(
                BasicBlock(
                    begin_address,
                    end_address
                )
            )
            
            line.tokens = [RT('for'), LPT(), LHRT(lines[other_index].tokens[0].next_value_register),
                RT(' in '), RHRT(line.tokens[0].obj_register), RPT()]
            lines[index + 1].tokens = []
            lines[other_index].tokens = []
            lines[other_index + 1].tokens = []
            
            continue
