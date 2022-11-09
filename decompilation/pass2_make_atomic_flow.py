#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Tuple, Dict, Set, Sequence, Union, Optional, Any
from os.path import dirname, realpath

from defs import HermesDecompiler, DecompiledFunctionBody, TokenString, LeftParenthsisToken, RightParenthesisToken, LeftHandRegToken, AssignmentToken, DotAccessorToken, CatchBlockStart, RightHandRegToken, BuiltinFunctionToken, FunctionToken, RawToken

class Pass2MakeAtomicFlow:
    
    def __init__(self, state : HermesDecompiler):
        
        state.function_id_to_body = {}
        
        TS = TokenString
        LHRT = LeftHandRegToken
        AT = AssignmentToken
        RHRT = RightHandRegToken
        RT = RawToken
        DAT = DotAccessorToken
        BFT = BuiltinFunctionToken
        CBS = CatchBlockStart
        FT = FunctionToken
        LPT = LeftParenthesisToken
        RPT = RawParenthesisToken
        
        for function_count, function_header in enumerate(state.hbc_reader.function_headers):
            
            function_body = DecompiledFunctionBody()
            function_body.function_name = hbc_reader.strings[function_header.functionName]
            function_body.function_object = function_header
            
            state.function_id_to_body[function_count] = function_body
            
            lines = function_body.statements = []
            
            for instruction in state.hbc_reader.function_ops[function_count]:
                
                op1 = getattr(instruction.inst, 'arg1', None)
                op2 = getattr(instruction.inst, 'arg2', None)
                op3 = getattr(instruction.inst, 'arg3', None)
                op4 = getattr(instruction.inst, 'arg4', None)
                op5 = getattr(instruction.inst, 'arg5', None)
                op6 = getattr(instruction.inst, 'arg6', None)
                
                if instruction.inst.name == 'Add':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' + '), RHRT(op3)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'Add32':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' + '), RHRT(op3),
                        RT(' | 0')],
                        assembly = [instruction]))
                elif instruction.inst.name == 'AddEmptyString':
                    lines.append(TS(LHRT(op1), AT(), RT("'' + "), RHRT(op2)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'AsyncBreakCheck':
                    pass
                elif instruction.inst.name == 'BitAnd':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' & '), RHRT(op3)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'BitNot':
                    lines.append(TS([LHRT(op1), AT(), RT('~'), RHRT(op2)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'BitOr':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' | '), RHRT(op3)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'BitXor':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' ^ '), RHRT(op3)],
                        assembly = [instruction]))
                # Note: It should be checker lather whether the implementation of
                # parsing the "Call*" opcodes present below matches the difference
                # between the function_header.frameSize and the latest frame
                # register index across all version of the Hermes bytecode VM,
                # whether thisArg is handled correctly in all implementation of
                # the variants of the call, we should also eventually set up
                # unit tests, etc.
                elif instruction.inst.name in ('Call', 'CallLong'):
                    args = []
                    for register in reversed(range(
                        function_header.frameSize - 7 - op3,
                        function_header.frameSize - 7)):
                        args += [RHRT(register), RT(', ')]
                    lines.append(TS([LHRT(op1), AT(),
                            RHRT(function_header.frameSize - 7), DAT(), RHRT(op2),
                            LPT(), *args[:-1], RPT()],
                        assembly = [instruction]))
                elif instruction.inst.name in ('Call1', 'Call2', 'Call3', 'Call4'):
                    args = []
                    for arg_count in range(1, len(int(instruction.inst.name[-1]))):
                        args += [RHRT([op4, op5, op6][arg_count]), RT(', ')]
                    lines.append(TS([LHRT(op1), AT(),
                            RHRT(op3), DAT(), RHRT(op2),
                            LPT(), *args[:-1], RPT()],
                        assembly = [instruction]))
                elif instruction.inst.name in ('CallDirect', 'CallDirectLongIndex'):
                    args = []
                    for register in reversed(range(
                        function_header.frameSize - 7 - op2,
                        function_header.frameSize - 7)):
                        args += [RHRT(register), RT(', ')]
                    lines.append(TS([LHRT(op1), AT(),
                            RHRT(function_header.frameSize - 7), DAT(), FT(op3),
                            LPT(), *args[:-1], RPT()],
                        assembly = [instruction]))
                elif instruction.inst.name in ('CallBuiltin', 'CallBuiltinLong'):
                    args = []
                    for register in reversed(range(
                        function_header.frameSize - 6 - op3,
                        function_header.frameSize - 6)):
                        args += [RHRT(register), RT(', ')]
                    lines.append(TS([LHRT(op1), AT(), BFT(op2), LPT(), *args[:-1], RPT()],
                        assembly = [instruction]))
                else:
                    raise NotImplementedError('[Unsupported instruction in function "%s":] %r' % (
                        function_body.function_name,
                        instruction
                    ))
                    
                    
        
        # WIP ..
