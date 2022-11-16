#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Tuple, Dict, Set, Sequence, Union, Optional, Any
from os.path import dirname, realpath

from defs import HermesDecompiler, DecompiledFunctionBody, TokenString, LeftParenthesisToken, RightParenthesisToken, LeftHandRegToken, AssignmentToken, DotAccessorToken, CatchBlockStart, RightHandRegToken, GetEnvironmentToken, NewEnvironmentToken, FunctionTableIndex, RawToken

class Pass2MakeAtomicFlow:
    
    def __init__(self, state : HermesDecompiler):
        
        state.function_id_to_body = {}
        
        TS = TokenString
        
        LHRT = LeftHandRegToken
        AT = AssignmentToken
        RHRT = RightHandRegToken
        RT = RawToken
        
        GET = GetEnvironmentToken
        NET = NewEnvironmentToken
        
        DAT = DotAccessorToken
        CBS = CatchBlockStart
        
        """
        BFT = BuiltinFunctionToken
        ACT = AsyncClosureToken
        CT = ClosureToken
        FT = FunctionToken
        """
        FTI = FunctionTableIndex
        
        LPT = LeftParenthesisToken
        RPT = RightParenthesisToken
        
        for function_count, function_header in enumerate(state.hbc_reader.function_headers):
            
            function_body = DecompiledFunctionBody()
            function_body.function_name = state.hbc_reader.strings[function_header.functionName]
            function_body.function_object = function_header
            
            state.function_id_to_body[function_count] = function_body
            
            lines = function_body.statements = []
            
            for instruction in state.hbc_reader.function_ops[function_count]:
                
                op1 = getattr(instruction, 'arg1', None)
                op2 = getattr(instruction, 'arg2', None)
                op3 = getattr(instruction, 'arg3', None)
                op4 = getattr(instruction, 'arg4', None)
                op5 = getattr(instruction, 'arg5', None)
                op6 = getattr(instruction, 'arg6', None)
                
                if instruction.inst.name == 'Add':  
                    lines.append(TS([LHRT(op1), AT(), RT('__uasm.add32'), LPT(), RHRT(op2), RT(', '), RHRT(op3), RPT()],
                        assembly = [instruction]))
                elif instruction.inst.name == 'AddEmptyString':
                    lines.append(TS([LHRT(op1), AT(), RT("'' + "), RHRT(op2)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'AsyncBreakCheck':
                    lines.append(TS([], assembly = [instruction]))
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
                    for arg_count in range(1, int(instruction.inst.name[-1])):
                        args += [RHRT([op4, op5, op6][arg_count - 1]), RT(', ')]
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
                            RHRT(function_header.frameSize - 7), DAT(), FTI(op3),
                            LPT(), *args[:-1], RPT()],
                        assembly = [instruction]))
                elif instruction.inst.name in ('CallBuiltin', 'CallBuiltinLong'):
                    args = []
                    for register in reversed(range(
                        function_header.frameSize - 6 - op3,
                        function_header.frameSize - 6)):
                        args += [RHRT(register), RT(', ')]
                    lines.append(TS([LHRT(op1), AT(), FTI(op2, is_builtin = True), LPT(), *args[:-1], RPT()],
                        assembly = [instruction]))
                elif instruction.inst.name == 'Catch':
                    lines.append(TS([CBS(op1)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'CoerceThisNS':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'CompleteGenerator':
                    lines.append(TS([], assembly = [instruction]))
                elif instruction.inst.name in ('Construct', 'ConstructLong'):
                    args = []
                    for register in reversed(range(
                        function_header.frameSize - 7 - op3,
                        function_header.frameSize - 7)):
                        args += [RHRT(register), RT(', ')]
                    lines.append(TS([LHRT(op1), AT(),
                            RT('new '), RHRT(function_header.frameSize - 7), DAT(), RHRT(op2),
                            LPT(), *args[:-1], RPT()],
                        assembly = [instruction]))
                elif instruction.inst.name in ('CreateAsyncClosure', 'CreateAsyncClosureLongIndex'):
                    lines.append(TS([LHRT(op1), AT(), FTI(op3, op2, is_async = True, is_closure = True)],
                        assembly = [instruction]))
                elif instruction.inst.name in ('CreateClosure', 'CreateClosureLongIndex'):
                    lines.append(TS([LHRT(op1), AT(), FTI(op3, op2, is_closure = True)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'CreateEnvironment':
                    lines.append(TS([NET(op1)],
                        assembly = [instruction]))
                elif instruction.inst.name in ('CreateGenerator', 'CreateGeneratorLongIndex'):
                    lines.append(TS([LHRT(op1), AT(), FTI(op3, op2, is_generator = True)],
                        assembly = [instruction]))
                elif instruction.inst.name in ('CreateGeneratorClosure', 'CreateGeneratorClosureLongIndex'):
                    lines.append(TS([LHRT(op1), AT(), FTI(op3, op2, is_closure = True, is_generator = True)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'CreateRegExp':
                    pattern_string = state.hbc_reader.strings[op2]
                    flags_string = state.hbc_reader.strings[op3]
                    
                    pattern_string = pattern_string.encode('unicode_escape').decode('ascii')
                    pattern_string = pattern_string.replace('/', '\\/')
                    
                    readable_regexp = '/%s/%s' % (
                        pattern_string,
                        flags_string
                    )
                    
                    lines.append(TS([LHRT(op1), AT(), RT(readable_regexp)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'CreateThis':
                    lines.append(TS([], assembly = [instruction]))
                elif instruction.inst.name == 'Debugger':
                    lines.append(TS([RT('debugger')], assembly = [instruction]))
                elif instruction.inst.name == 'DebuggerBreakCheck':
                    lines.append(TS([], assembly = [instruction]))
                elif instruction.inst.name == 'Dec':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' - 1')], assembly = [instruction]))
                elif instruction.inst.name == 'DeclareGlobalVar':
                    global_var = state.hbc_reader.strings[op1]
                    
                    lines.append(TS([RT(global_var), AT(), RT('undefined')], assembly = [instruction]))
                elif instruction.inst.name in ('DelById', 'DelByIdLong'):
                    prop_string = state.hbc_reader.strings[op3]
                    
                    lines.append(TS([LHRT(op1), AT(), RT('delete '), RHRT(op2), DAT(), RT(prop_string)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'DelByVal':
                    lines.append(TS([LHRT(op1), AT(), RT('delete '), RHRT(op2), DAT(), RHRT(op3)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'DirectEval':
                    lines.append(TS([LHRT(op1), AT(), RT('eval'), LPT(), RHRT(op2), RPT()],
                        assembly = [instruction]))
                elif instruction.inst.name in ('Div', 'DivN'):
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' / '), RHRT(op3)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'Divi32':
                    lines.append(TS([LHRT(op1), AT(), RT('__uasm.divi32'), LPT(), RHRT(op2), RT(', '), RHRT(op3), RPT()],
                        assembly = [instruction]))
                elif instruction.inst.name == 'Divu32':
                    lines.append(TS([LHRT(op1), AT(), RT('__uasm.divu32'), LPT(), RHRT(op2), RT(', '), RHRT(op3), RPT()],
                        assembly = [instruction]))
                elif instruction.inst.name == 'Eq':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT('=='), RHRT(op3)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'GetArgumentsLength':
                    lines.append(TS([LHRT(op1), AT(), RT('arguments.length')],
                        assembly = [instruction]))
                elif instruction.inst.name == 'GetArgumentsPropByVal':
                    lines.append(TS([LHRT(op1), AT(), RT('arguments'), DAT(), RHRT(op2)],
                        assembly = [instruction]))
                    # WIP ..
                elif instruction.inst.name == 'GetBuiltinClosure':
                    lines.append(TS([LHRT(op1), AT(), FTI(op2, is_builtin = True, is_closure = True)],
                        assembly = [instruction]))
                elif instruction.inst.name in ('GetById', 'GetByIdLong', 'GetByIdShort'):
                    string = state.hbc_reader.strings[instruction.inst.name]
                    
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), DAT(), RT(string)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'GetByVal':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), DAT(), RHRT(op3)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'GetEnvironment':
                    lines.append(TS([GET(op1, op2)], assembly = [instruction]))
                elif instruction.inst.name == 'GetGlobalObject':
                    lines.append(TS([LHRT(op1), AT(), RT('global')], assembly = [instruction]))
                elif instruction.inst.name == 'GetNewTarget':
                    lines.append(TS([LHRT(op1), AT(), RT('new.target')], assembly = [instruction]))
                elif instruction.inst.name == 'GetNextPName':
                    lines.append(TS([
                else:
                    lines.append(TS([RT('// Unsupported instruction: %r' % instruction)],
                        assembly = [instruction]))
                    """
                    # Todo: We should likely put an "Error comment" in the decompiled
                    # source later, instead of this
                    raise NotImplementedError('[Unsupported instruction in function "%s":] %r' % (
                        function_body.function_name,
                        instruction
                    ))
                    """
                    
                    
        
        # WIP ..
