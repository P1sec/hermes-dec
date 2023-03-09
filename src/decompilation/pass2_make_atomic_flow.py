#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Tuple, Dict, Set, Sequence, Union, Optional, Any
from os.path import dirname, realpath

from defs import HermesDecompiler, DecompiledFunctionBody, TokenString, LeftParenthesisToken, RightParenthesisToken, LeftHandRegToken, AssignmentToken, DotAccessorToken, CatchBlockStart, RightHandRegToken, GetEnvironmentToken, StoreToEnvironment, BindToken, SwitchImm, LoadFromEnvironmentToken, ReturnDirective, ResumeGenerator, SaveGenerator, StartGenerator, NewEnvironmentToken, JumpCondition, JumpNotCondition, FunctionTableIndex, ForInLoopInit, ForInLoopNextIter, ThrowDirective, ReturnDirective, RawToken
from serialized_literal_parser import unpack_slp_array, SLPArray, SLPValue, TagType

class Pass2MakeAtomicFlow:
    
    def __init__(self, state : HermesDecompiler):
        
        TS = TokenString
        
        RD = ReturnDirective
        BIND = BindToken
        
        RG = ResumeGenerator
        SG = SaveGenerator
        SG2 = StartGenerator

        LHRT = LeftHandRegToken
        AT = AssignmentToken
        RHRT = RightHandRegToken
        RT = RawToken
        
        GET = GetEnvironmentToken
        STE = StoreToEnvironment
        NET = NewEnvironmentToken
        LFET = LoadFromEnvironmentToken
        
        TD = ThrowDirective
        RD = ReturnDirective
        
        SI = SwitchImm
        JC = JumpCondition
        JNC = JumpNotCondition
        
        FILI = ForInLoopInit
        FILNI = ForInLoopNextIter
        
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
            
            function_body = state.function_id_to_body[function_count]

            lines = function_body.statements = []
            
            for instruction in state.hbc_reader.function_ops[function_count]:
                
                op1 = getattr(instruction, 'arg1', None)
                op2 = getattr(instruction, 'arg2', None)
                op3 = getattr(instruction, 'arg3', None)
                op4 = getattr(instruction, 'arg4', None)
                op5 = getattr(instruction, 'arg5', None)
                op6 = getattr(instruction, 'arg6', None)
                
                if instruction.inst.name in ('Add', 'AddN'):
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' + '), RHRT(op3)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'Add32':
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
                # Note: It should be checked later whether the implementation of
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
                            RHRT(function_header.frameSize - 7), RT('['), RHRT(op2), RT(']'),
                            LPT(), *args[:-1], RPT()],
                        assembly = [instruction]))
                elif instruction.inst.name in ('Call1', 'Call2', 'Call3', 'Call4'):
                    args = []
                    for arg_count in range(1, int(instruction.inst.name[-1])):
                        args += [RHRT([op4, op5, op6][arg_count - 1]), RT(', ')]
                    lines.append(TS([LHRT(op1), AT(),
                            RHRT(op2), BIND(op3),
                            LPT(), *args[:-1], RPT()],
                        assembly = [instruction]))
                elif instruction.inst.name in ('CallDirect', 'CallDirectLongIndex'):
                    args = []
                    for register in reversed(range(
                        function_header.frameSize - 7 - op2,
                        function_header.frameSize - 7)):
                        args += [RHRT(register), RT(', ')]
                    lines.append(TS([LHRT(op1), AT(),
                            DAT(), FTI(op3, state), BIND(function_header.frameSize - 7),
                            LPT(), *args[:-1], RPT()],
                        assembly = [instruction]))
                elif instruction.inst.name in ('CallBuiltin', 'CallBuiltinLong'):
                    args = []
                    for register in reversed(range(
                        function_header.frameSize - 7 - (op3 - 1),
                        function_header.frameSize - 7)):
                        args += [RHRT(register), RT(', ')]
                    lines.append(TS([LHRT(op1), AT(), FTI(op2, state, is_builtin = True), LPT(), *args[:-1], RPT()],
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
                            RT('new '), RHRT(function_header.frameSize - 7), RT('['), RHRT(op2), RT(']'),
                            LPT(), *args[:-1], RPT()],
                        assembly = [instruction]))
                elif instruction.inst.name in ('CreateAsyncClosure', 'CreateAsyncClosureLongIndex'):
                    lines.append(TS([LHRT(op1), AT(), FTI(op3, state, op2, is_async = True, is_closure = True)],
                        assembly = [instruction]))
                elif instruction.inst.name in ('CreateClosure', 'CreateClosureLongIndex'):
                    lines.append(TS([LHRT(op1), AT(), FTI(op3, state, op2, is_closure = True)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'CreateEnvironment':
                    lines.append(TS([NET(op1)],
                        assembly = [instruction]))
                elif instruction.inst.name in ('CreateGenerator', 'CreateGeneratorLongIndex'):
                    lines.append(TS([LHRT(op1), AT(), FTI(op3, state, op2, is_generator = True)],
                        assembly = [instruction]))
                elif instruction.inst.name in ('CreateGeneratorClosure', 'CreateGeneratorClosureLongIndex'):
                    lines.append(TS([LHRT(op1), AT(), FTI(op3, state, op2, is_closure = True, is_generator = True)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'CreateRegExp':
                    pattern_string = state.hbc_reader.strings[op2]
                    flags_string = state.hbc_reader.strings[op3]
                    
                    pattern_string = pattern_string.translate({
                        char: repr(char) for char in range(0x20)
                    })
                    pattern_string = pattern_string.replace('/', '\\/')
                    
                    readable_regexp = '/%s/%s' % (
                        pattern_string,
                        flags_string
                    )
                    
                    lines.append(TS([LHRT(op1), AT(), RT(readable_regexp)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'CreateThis':
                    lines.append(TS([LHRT(op1), AT(), RT('Object.create'), LPT(),
                        RHRT(op2), RT(', {constructor: {value: '), RHRT(op3), RT('}}'),
                            RPT()], assembly = [instruction]))
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
                    lines.append(TS([LHRT(op1), AT(), RT('delete '), RHRT(op2), RT('['), RHRT(op3), RT(']')],
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
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' == '), RHRT(op3)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'GetArgumentsLength':
                    lines.append(TS([LHRT(op1), AT(), RT('arguments.length')],
                        assembly = [instruction]))
                elif instruction.inst.name == 'GetArgumentsPropByVal':
                    lines.append(TS([LHRT(op1), AT(), RT('arguments'), RT('['), RHRT(op2), RT(']')],
                        assembly = [instruction]))
                elif instruction.inst.name == 'GetBuiltinClosure':
                    lines.append(TS([LHRT(op1), AT(), FTI(op2, state, is_builtin = True, is_closure = True)],
                        assembly = [instruction]))
                elif instruction.inst.name in ('GetById', 'GetByIdLong', 'GetByIdShort',
                    'TryGetById', 'TryGetByIdLong'):
                    string = state.hbc_reader.strings[op4]
                    
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), DAT(), RT(string)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'GetByVal':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT('['), RHRT(op3), RT(']')],
                        assembly = [instruction]))
                elif instruction.inst.name == 'GetEnvironment':
                    lines.append(TS([GET(op1, op2)], assembly = [instruction]))
                elif instruction.inst.name == 'GetGlobalObject':
                    lines.append(TS([LHRT(op1), AT(), RT('global')], assembly = [instruction]))
                elif instruction.inst.name == 'GetNewTarget':
                    lines.append(TS([LHRT(op1), AT(), RT('new.target')], assembly = [instruction]))
                elif instruction.inst.name == 'GetNextPName':
                    lines.append(TS([FILNI(op1, op2, op3, op4, op5)], assembly = [instruction]))
                elif instruction.inst.name == 'GetPNameList':
                    lines.append(TS([FILI(op1, op2, op3, op4)], assembly = [instruction]))
                elif instruction.inst.name == 'Greater':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' > '), RHRT(op3)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'GreaterEq':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' >= '), RHRT(op3)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'Inc':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' + 1')],
                        assembly = [instruction]))
                elif instruction.inst.name == 'InstanceOf':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' instanceof '), RHRT(op3)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'IsIn':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' in '), RHRT(op3)],
                        assembly = [instruction]))
                # Note: The implementations of the methods related to the iteration below
                # is not fully consistent with the corresponding React Native instruction
                # behavior, which has special handling for iterating over arrays, may
                # suppress propagating the exception over certain IteratorClose() calls...
                #
                # This may be improved in the future if any required.
                elif instruction.inst.name == 'IteratorBegin':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT('[Symbol.iterator]')],
                        assembly = [instruction]))
                    lines.append(TS([LHRT(op2), AT(), RHRT(op1), LPT(), RPT(), DAT(), RT('next')],
                        assembly = [instruction]))
                elif instruction.inst.name == 'IteratorNext':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op3), LPT(), RPT(), DAT(), RT('value')],
                        assembly = [instruction]))
                elif instruction.inst.name == 'IteratorClose':
                    lines.append(TS([RHRT(op1), DAT(), RT('return'), LPT(), RPT()],
                        assembly = [instruction]))
                elif instruction.inst.name in ('JEqual', 'JEqualLong'):
                    if op1 > 0:
                        lines.append(TS([JNC(instruction.original_pos + op1), RHRT(op2), RT(' != '), RHRT(op3)],
                            assembly = [instruction]))
                    else:
                        lines.append(TS([JC(instruction.original_pos + op1), RHRT(op2), RT(' == '), RHRT(op3)],
                            assembly = [instruction]))
                elif instruction.inst.name in ('JGreater', 'JGreaterN', 'JGreaterLong', 'JGreaterNLong'):
                    if op1 > 0:
                        lines.append(TS([JNC(instruction.original_pos + op1), RT('!'), LPT(), RHRT(op2), RT(' > '), RHRT(op3), RPT()],
                            assembly = [instruction]))
                    else:
                        lines.append(TS([JC(instruction.original_pos + op1), RHRT(op2), RT(' > '), RHRT(op3)],
                            assembly = [instruction]))
                elif instruction.inst.name in ('JNotGreater', 'JNotGreaterN', 'JNotGreaterLong', 'JNotGreaterNLong'):
                    if op1 > 0:
                        lines.append(TS([JNC(instruction.original_pos + op1), RHRT(op2), RT(' > '), RHRT(op3)],
                            assembly = [instruction]))
                    else:
                        lines.append(TS([JC(instruction.original_pos + op1), RT('!'), LPT(), RHRT(op2), RT(' > '), RHRT(op3), RPT()],
                            assembly = [instruction]))
                elif instruction.inst.name in ('JGreaterEqual', 'JGreaterEqualN', 'JGreaterEqualLong', 'JGreaterEqualNLong'):
                    if op1 > 0:
                        lines.append(TS([JNC(instruction.original_pos + op1), RT('!'), LPT(), RHRT(op2), RT(' >= '), RHRT(op3), RPT()],
                            assembly = [instruction]))
                    else:
                        lines.append(TS([JC(instruction.original_pos + op1), RHRT(op2), RT(' >= '), RHRT(op3)],
                            assembly = [instruction]))
                elif instruction.inst.name in ('JNotGreaterEqual', 'JNotGreaterEqualN', 'JNotGreaterEqualLong', 'JNotGreaterEqualNLong'):
                    if op1 > 0:
                        lines.append(TS([JNC(instruction.original_pos + op1), RHRT(op2), RT(' >= '), RHRT(op3)],
                            assembly = [instruction]))
                    else:
                        lines.append(TS([JC(instruction.original_pos + op1), RT('!'), LPT(), RHRT(op2), RT(' >= '), RHRT(op3), RPT()],
                            assembly = [instruction]))
                elif instruction.inst.name in ('JLess', 'JLessN', 'JLessLong', 'JLessNLong'):
                    if op1 > 0:
                        lines.append(TS([JNC(instruction.original_pos + op1), RT('!'), LPT(), RHRT(op2), RT(' < '), RHRT(op3), RPT()],
                            assembly = [instruction]))
                    else:
                        lines.append(TS([JC(instruction.original_pos + op1), RHRT(op2), RT(' < '), RHRT(op3)],
                            assembly = [instruction]))
                elif instruction.inst.name in ('JNotLess', 'JNotLessN', 'JNotLessLong', 'JNotLessNLong'):
                    if op1 > 0:
                        lines.append(TS([JNC(instruction.original_pos + op1), RHRT(op2), RT(' < '), RHRT(op3)],
                            assembly = [instruction]))
                    else:
                        lines.append(TS([JC(instruction.original_pos + op1), RT('!'), LPT(), RHRT(op2), RT(' < '), RHRT(op3), RPT()],
                            assembly = [instruction]))
                elif instruction.inst.name in ('JLessEqual', 'JLessEqualN', 'JLessEqualLong', 'JLessEqualNLong'):
                    if op1 > 0:
                        lines.append(TS([JNC(instruction.original_pos + op1), RT('!'), LPT(), RHRT(op2), RT(' <= '), RHRT(op3), RPT()],
                            assembly = [instruction]))
                    else:
                        lines.append(TS([JC(instruction.original_pos + op1), RHRT(op2), RT(' <= '), RHRT(op3)],
                            assembly = [instruction]))
                elif instruction.inst.name in ('JNotLessEqual', 'JNotLessEqualN', 'JNotLessEqualLong', 'JNotLessEqualNLong'):
                    if op1 > 0:
                        lines.append(TS([JNC(instruction.original_pos + op1), RHRT(op2), RT(' <= '), RHRT(op3)],
                            assembly = [instruction]))
                    else:
                        lines.append(TS([JC(instruction.original_pos + op1), RT('!'), LPT(), RHRT(op2), RT(' <= '), RHRT(op3), RPT()],
                            assembly = [instruction]))
                elif instruction.inst.name in ('JNotEqual', 'JNotEqualLong'):
                    if op1 > 0:
                        lines.append(TS([JNC(instruction.original_pos + op1), RHRT(op2), RT(' == '), RHRT(op3)],
                            assembly = [instruction]))
                    else:
                        lines.append(TS([JC(instruction.original_pos + op1), RHRT(op2), RT(' != '), RHRT(op3)],
                            assembly = [instruction]))
                elif instruction.inst.name in ('JStrictEqual', 'JStrictEqualLong'):
                    if op1 > 0:
                        lines.append(TS([JNC(instruction.original_pos + op1), RHRT(op2), RT(' !== '), RHRT(op3)],
                            assembly = [instruction]))
                    else:
                        lines.append(TS([JC(instruction.original_pos + op1), RHRT(op2), RT(' === '), RHRT(op3)],
                            assembly = [instruction]))
                elif instruction.inst.name in ('JStrictNotEqual', 'JStrictNotEqualLong'):
                    if op1 > 0:
                        lines.append(TS([JNC(instruction.original_pos + op1), RHRT(op2), RT(' === '), RHRT(op3)],
                            assembly = [instruction]))
                    else:
                        lines.append(TS([JC(instruction.original_pos + op1), RHRT(op2), RT(' !== '), RHRT(op3)],
                            assembly = [instruction]))
                elif instruction.inst.name in ('Jmp', 'JmpLong'):
                    if op1 > 0:
                        lines.append(TS([JNC(instruction.original_pos + op1), RT('false')],
                            assembly = [instruction]))
                    else:
                        lines.append(TS([JC(instruction.original_pos + op1), RT('true')],
                            assembly = [instruction]))
                elif instruction.inst.name in ('JmpFalse', 'JmpFalseLong'):
                    if op1 > 0:
                        lines.append(TS([JNC(instruction.original_pos + op1), RHRT(op2)],
                            assembly = [instruction]))
                    else:
                        lines.append(TS([JC(instruction.original_pos + op1), RT('!'), RHRT(op2)],
                            assembly = [instruction]))
                elif instruction.inst.name in ('JmpTrue', 'JmpTrueLong'):
                    if op1 > 0:
                        lines.append(TS([JNC(instruction.original_pos + op1), RT('!'), RHRT(op2)],
                            assembly = [instruction]))
                    else:
                        lines.append(TS([JC(instruction.original_pos + op1), RHRT(op2)],
                            assembly = [instruction]))
                elif instruction.inst.name in ('JmpUndefined', 'JmpUndefinedLong'):
                    if op1 > 0:
                        lines.append(TS([JNC(instruction.original_pos + op1), RHRT(op2), RT(' !== undefined')],
                            assembly = [instruction]))
                    else:
                        lines.append(TS([JC(instruction.original_pos + op1), RHRT(op2), RT(' === undefined')],
                            assembly = [instruction]))
                elif instruction.inst.name == 'LShift':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' << '), RHRT(op3)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'Less':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' < '), RHRT(op3)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'LessEq':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' <= '), RHRT(op3)],
                        assembly = [instruction]))
                elif instruction.inst.name in ('LoadConstBigInt', 'LoadConstBigIntLongIndex'):
                    lines.append(TS([LHRT(op1), AT(), RT(str(state.hbc_reader.bigint_values[op2]) + 'n')],
                        assembly = [instruction])) # TODO : Decode BigInts correctly
                elif instruction.inst.name in ('LoadConstDouble', 'LoadConstInt', 'LoadConstUInt8'):
                    lines.append(TS([LHRT(op1), AT(), str(op2)],
                        assembly = [instruction]))
                elif instruction.inst.name in ('LoadConstEmpty', 'LoadConstUndefined'):
                    lines.append(TS([LHRT(op1), AT(), RT('undefined')],
                        assembly = [instruction]))
                elif instruction.inst.name == 'LoadConstFalse':
                    lines.append(TS([LHRT(op1), AT(), RT('false')],
                        assembly = [instruction]))
                elif instruction.inst.name == 'LoadConstNull':
                    lines.append(TS([LHRT(op1), AT(), RT('null')],
                        assembly = [instruction]))
                elif instruction.inst.name in ('LoadConstString', 'LoadConstStringLongIndex'):
                    lines.append(TS([LHRT(op1), AT(), RT(repr(state.hbc_reader.strings[op2]))],
                        assembly = [instruction]))
                elif instruction.inst.name == 'LoadConstTrue':
                    lines.append(TS([LHRT(op1), AT(), RT('true')],
                        assembly = [instruction]))
                elif instruction.inst.name == 'LoadConstZero':
                    lines.append(TS([LHRT(op1), AT(), RT('0')],
                        assembly = [instruction]))
                elif instruction.inst.name in ('LoadFromEnvironment', 'LoadFromEnvironmentL'):
                    lines.append(TS([LHRT(op1), AT(), LFET(op2, op3)],
                        assembly = [instruction]))
                elif instruction.inst.name in ('LoadParam', 'LoadParamLong'):
                    if not op2:
                        arg_name = 'this'
                    elif op2 < function_body.function_object.paramCount:
                        arg_name = 'a' + str(op2 - 1)
                    else:
                        arg_name = 'arguments[%d]' % (op2 - 1)
                    lines.append(TS([LHRT(op1), AT(), RT(arg_name)],
                            assembly = [instruction]))
                elif instruction.inst.name == 'LoadThisNS':
                    lines.append(TS([LHRT(op1), AT(), RT('this')],
                        assembly = [instruction]))
                elif instruction.inst.name in ('Loadi16', 'Loadi32', 'Loadi8', 'Loadu16', 'Loadu32', 'Loadu8'):
                    lines.append(TS([LHRT(op1), AT(), RT('__uasm.' + instruction.inst.name.lower()), LPT(), RHRT(op2), RT(', '), RHRT(op3), RPT()],
                        assembly = [instruction]))
                elif instruction.inst.name == 'Mod':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' % '), RHRT(op3)],
                        assembly = [instruction]))
                elif instruction.inst.name in ('Mov', 'MovLong'):
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'Mul32':
                    lines.append(TS([LHRT(op1), AT(), RT('__uasm.mul32'), LPT(), RHRT(op2), RT(', '), RHRT(op3), RPT()],
                        assembly = [instruction]))
                elif instruction.inst.name in ('Mul', 'MulN'):
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' * '), RHRT(op3)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'Negate':
                    lines.append(TS([LHRT(op1), AT(), RT('-'), RHRT(op2)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'Neq':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' != '), RHRT(op3)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'NewArray':
                    lines.append(TS([LHRT(op1), AT(), RT('new Array'), LPT(), RT(str(op2)), RPT()],
                        assembly = [instruction]))
                elif instruction.inst.name in ('NewArrayWithBuffer', 'NewArrayWithBufferLong'):
                    array_text = '[%s]' % ', '.join(unpack_slp_array(
                        state.hbc_reader.arrays[op4:], op3).to_strings(state.hbc_reader.strings))
                    lines.append(TS([LHRT(op1), AT(), RT(array_text)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'NewObject':
                    lines.append(TS([LHRT(op1), AT(), RT('{}')],
                        assembly = [instruction]))
                elif instruction.inst.name in ('NewObjectWithBuffer', 'NewObjectWithBufferLong'):
                    object_text = '{%s}' % ', '.join('%s: %s' % (key, value)
                        for key, value in zip(
                            unpack_slp_array(state.hbc_reader.object_keys[op4:], op3).to_strings(state.hbc_reader.strings),
                            unpack_slp_array(state.hbc_reader.object_values[op5:], op3).to_strings(state.hbc_reader.strings)
                        ))
                    lines.append(TS([LHRT(op1), AT(), RT(object_text)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'NewObjectWithParent':
                    lines.append(TS([LHRT(op1), AT(), RT('Object.create'), LPT(), RHRT(op2), RPT()],
                        assembly = [instruction]))
                elif instruction.inst.name == 'Not':
                    lines.append(TS([LHRT(op1), AT(), RT('-'), RHRT(op2)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'ProfilePoint':
                    lines.append(TS([], assembly = [instruction]))
                elif instruction.inst.name in ('PutById', 'PutByIdLong',
                    'TryPutById', 'TryPutByIdLong'):
                    index = repr(state.hbc_reader.strings[op4])
                    lines.append(TS([LHRT(op1), RT('[' + index + ']'), AT(), RHRT(op2)],
                        assembly = [instruction]))
                elif instruction.inst.name in ('PutNewOwnById', 'PutNewOwnByIdLong',
                    'PutNewOwnByIdShort'):
                    index = repr(state.hbc_reader.strings[op3])
                    lines.append(TS([LHRT(op1), RT('[' + index + ']'), AT(), RHRT(op2)],
                        assembly = [instruction]))
                elif instruction.inst.name in ('PutNewOwnNEById', 'PutNewOwnNEByIdLong'):
                    index = repr(state.hbc_reader.strings[op3])
                    lines.append(TS([RT('Object.defineProperty'), LPT(),
                        LHRT(op1), RT(', '), RT(repr(index)),
                        RT(', {value: '), RHRT(op2), RT('}'), RPT()],
                        assembly = [instruction]))
                    # TODO: Are non-enumerable values set correctly?
                    # When are these used if they are used?
                elif instruction.inst.name == 'PutByVal':
                    lines.append(TS([LHRT(op1), RT('['), RHRT(op2), RT(']'), AT(), RHRT(op3)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'PutOwnByVal':
                    if op4: # Is the property enumerable?
                        lines.append(TS([LHRT(op1), RT('['), RHRT(op3), RT(']'), AT(), RHRT(op2)],
                            assembly = [instruction]))
                    else:
                        lines.append(TS([RT('Object.defineProperty'), LPT(),
                            LHRT(op1), RT(', '), RHRT(op3),
                            RT(', {value: '), RHRT(op2), RT('}'), RPT()],
                            assembly = [instruction]))
                elif instruction.inst.name in ('PutOwnByIndex', 'PutOwnByIndexL'):
                    lines.append(TS([LHRT(op1), RT('[%d]' % op3), AT(), RHRT(op2)],
                        assembly = [instruction]))
                elif instruction.inst.name in ('PutOwnGetterSetterByVal'):
                    index = repr(state.hbc_reader.strings[op3])
                    lines.append(TS([RT('Object.defineProperty'), LPT(),
                        LHRT(op1), RT(', '), RHRT(op2),
                        RT(', {get: '), RHRT(op3), RT(', set: '), RHRT(op4),
                        RT(', enumerable: ' + ('true' if op5 else 'false') + '}'), RPT()],
                        assembly = [instruction]))
                elif instruction.inst.name == 'RShift':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' >> '), RHRT(op3)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'ReifyArguments':
                    lines.append(TS([LHRT(op1), AT(), RT('arguments')],
                        assembly = [instruction]))
                elif instruction.inst.name == 'ResumeGenerator':
                    lines.append(TS([RG(op1, op2)], assembly = [instruction]))
                elif instruction.inst.name == 'Ret':
                    lines.append(TS([RD(), RHRT(op1)], assembly = [instruction]))
                elif instruction.inst.name in ('SaveGenerator', 'SaveGeneratorLong'):
                    lines.append(TS([SG(instruction.original_pos + op1)], assembly = [instruction]))
                elif instruction.inst.name == 'SelectObject':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op3), RT(' instanceof Object ? '),
                        RHRT(op3), RT(' : '), RHRT(op2)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'StartGenerator':
                    lines.append(TS([SG2()], assembly = [instruction]))
                elif instruction.inst.name in ('Store16', 'Store32', 'Store8'):
                    lines.append(TS([RT('__uasm.' + instruction.inst.name.lower()), LPT(), RHRT(op1), RT(', '), RHRT(op2), RT(', '), RHRT(op3), RPT()],
                        assembly = [instruction]))
                elif instruction.inst.name in ('StoreNPToEnvironment', 'StoreNPToEnvironmentL',
                    'StoreToEnvironment', 'StoreToEnvironmentL'):
                    lines.append(TS([STE(op1, op2, op3)], assembly = [instruction]))
                elif instruction.inst.name == 'StrictEq':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' === '), RHRT(op3)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'StrictNeq':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' !== '), RHRT(op3)],
                        assembly = [instruction]))
                elif instruction.inst.name in ('Sub', 'SubN'):
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' - '), RHRT(op3)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'Sub32':
                    lines.append(TS([LHRT(op1), AT(), RT('__uasm.sub32'), LPT(), RHRT(op2), RT(', '), RHRT(op3), RPT()],
                        assembly = [instruction]))
                elif instruction.inst.name == 'SwitchImm':
                    lines.append(TS([SI(op1, instruction.original_pos + op2,
                        instruction.original_pos + op3, op4, op5),
                        RT(' // Switch table: %s' % instruction.switch_jump_table)], assembly = [instruction]))
                elif instruction.inst.name == 'Throw':
                    lines.append(TS([TD(), RHRT(op1)], assembly = [instruction]))
                elif instruction.inst.name == 'ThrowIfEmpty':
                    lines.append(TS([RT('if'), LPT(), RT('!'), RHRT(op2), RPT(), RT(' '), TD(), RT('ReferenceError()')],
                        assembly = [instruction]))
                    lines.append(TS([RT('else '), LHRT(op1), AT(), RHRT(op2)], assembly = []))
                elif instruction.inst.name == 'ThrowIfUndefinedInst':
                    lines.append(TS([RT('if'), LPT(), RT('typeof '), RHRT(op1), RT(" === 'undefined'"),
                        RPT(), RT(' '), TD(), RT('ReferenceError()')],
                        assembly = [instruction]))
                elif instruction.inst.name == 'ToInt32':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' | 0')],
                        assembly = [instruction]))
                elif instruction.inst.name == 'ToNumber':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' - 0')],
                        assembly = [instruction]))
                elif instruction.inst.name == 'ToNumeric':
                    lines.append(TS([LHRT(op1), AT(), RT('parseFloat'), LPT(),
                        RHRT(op2), RPT()],
                        assembly = [instruction]))
                elif instruction.inst.name == 'TypeOf':
                    lines.append(TS([LHRT(op1), AT(), RT('typeof '), RHRT(op2)],
                        assembly = [instruction]))
                elif instruction.inst.name == 'URshift':
                    lines.append(TS([LHRT(op1), AT(), RHRT(op2), RT(' >>> '),
                        RHRT(op3)], assembly = [instruction]))
                elif instruction.inst.name == 'Unreachable':
                    raise ValueError('Unreachable position reached: %r' % instruction)

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
