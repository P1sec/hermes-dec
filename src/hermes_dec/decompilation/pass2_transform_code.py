#!/usr/bin/env python3
# -*- encoding: Utf-8 -*-
import re
from typing import List, Tuple, Dict, Set, Sequence, Union, Optional, Any
from os.path import dirname, realpath

from hermes_dec.decompilation.defs import (
    HermesDecompiler,
    DecompiledFunctionBody,
    TokenString,
    LeftParenthesisToken,
    RightParenthesisToken,
    LeftHandRegToken,
    AssignmentToken,
    DotAccessorToken,
    IndexStringToken,
    CatchBlockStart,
    RightHandRegToken,
    GetEnvironmentToken,
    StoreToEnvironment,
    BindToken,
    SwitchImm,
    LoadFromEnvironmentToken,
    ReturnDirective,
    ResumeGenerator,
    SaveGenerator,
    StartGenerator,
    NewInnerEnvironmentToken,
    NewEnvironmentToken,
    JumpCondition,
    JumpNotCondition,
    FunctionTableIndex,
    ForInLoopInit,
    ForInLoopNextIter,
    ThrowDirective,
    ReturnDirective,
    RawToken,
)
from hermes_dec.parsers.serialized_literal_parser import (
    unpack_slp_array,
    SLPArray,
    SLPValue,
    TagType,
)
from hermes_dec.parsers.hbc_bytecode_parser import parse_hbc_bytecode


# e.g. 3D, *, "unsigned long long"
invalid_js_property = re.compile('^[^_a-zA-Z]')

# Hermes internal TypeOfResult bitmask (JmpTypeOfIs / TypeOfIs operand)
_HERMES_TYPEOF_BITS = [
    (1,   'undefined'),
    (2,   'null'),
    (4,   'boolean'),
    (8,   'number'),
    (16,  'string'),
    (32,  'bigint'),
    (64,  'symbol'),
    (128, 'object'),
    (256, 'function'),
]


def _typeof_bitmask_info(bitmask):
    """Return (op, typename) for the positive-match comparison implied by bitmask.

    Returns ('===', name) for single-type masks, ('!==', excluded) for
    all-except-one masks, or None for complex multi-type masks.
    """
    matched = [(bit, name) for bit, name in _HERMES_TYPEOF_BITS if bitmask & bit]
    unmatched = [(bit, name) for bit, name in _HERMES_TYPEOF_BITS if not (bitmask & bit)]
    if len(matched) == 1:
        return ('===', matched[0][1])
    if len(unmatched) == 1:
        return ('!==', unmatched[0][1])
    return None


def _typeof_cond_tokens(bitmask, reg_op):
    """Return a token list expressing 'typeof reg matches bitmask' (positive sense).

    Used by JmpTypeOfIs and TypeOfIs handlers.  Caller must pass the complement
    bitmask when building the JNC (forward-jump) condition.
    Uses full token class names since this is module-level (aliases are local to pass2).
    """
    info = _typeof_bitmask_info(bitmask)
    if info:
        return [RawToken('typeof '), RightHandRegToken(reg_op), RawToken(" %s '%s'" % info)]

    # null (bit 1) is special in Hermes: internally distinct from non-null objects,
    # but typeof null === 'object' in JS so we express it as === null.
    matched_names = [n for bit, n in _HERMES_TYPEOF_BITS if bitmask & bit]
    has_null = 'null' in matched_names
    non_null = [n for n in matched_names if n != 'null']
    if len(non_null) == 1 and has_null:
        # e.g. 258 (null|function) → (typeof r === 'function' || r === null)
        return [LeftParenthesisToken(), RawToken('typeof '), RightHandRegToken(reg_op),
                RawToken(" === '%s' || " % non_null[0]),
                RightHandRegToken(reg_op), RawToken(' === null'), RightParenthesisToken()]

    # Check if the complement reduces to a null|single case (De Morgan)
    complement = 511 ^ bitmask
    comp_matched = [n for bit, n in _HERMES_TYPEOF_BITS if complement & bit]
    comp_has_null = 'null' in comp_matched
    comp_non_null = [n for n in comp_matched if n != 'null']
    if len(comp_non_null) == 1 and comp_has_null:
        # e.g. 253 = NOT(null|function) → (typeof r !== 'function' && r !== null)
        return [LeftParenthesisToken(), RawToken('typeof '), RightHandRegToken(reg_op),
                RawToken(" !== '%s' && " % comp_non_null[0]),
                RightHandRegToken(reg_op), RawToken(' !== null'), RightParenthesisToken()]

    return [RawToken("/* typeof mask=0x%x */ true" % bitmask)]


def pass2_transform_code(
    state: HermesDecompiler, function_body: DecompiledFunctionBody
):

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
    IST = IndexStringToken

    GET = GetEnvironmentToken
    STE = StoreToEnvironment
    NET = NewEnvironmentToken
    NIET = NewInnerEnvironmentToken
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

    lines = function_body.statements = []

    function_header = function_body.function_object

    # Pre-scan: find registers that hold actual environment objects.
    # CreateClosure/CreateGenerator sometimes receive an `undefined` register
    # (no captured env) rather than a real env register.  We must only link
    # FunctionTableIndex to an environment_id when the register was genuinely
    # populated by an env-creating instruction.
    _ENV_CREATORS = frozenset((
        'CreateEnvironment', 'CreateFunctionEnvironment', 'CreateTopLevelEnvironment',
        'CreateInnerEnvironment', 'GetClosureEnvironment', 'GetEnvironment', 'GetParentEnvironment',
    ))
    _env_registers: set = set()
    for _pre in parse_hbc_bytecode(function_header, state.hbc_reader):
        if _pre.inst.name in _ENV_CREATORS:
            _env_registers.add(_pre.arg1)

    for instruction in parse_hbc_bytecode(function_header, state.hbc_reader):
        op1 = getattr(instruction, 'arg1', None)
        op2 = getattr(instruction, 'arg2', None)
        op3 = getattr(instruction, 'arg3', None)
        op4 = getattr(instruction, 'arg4', None)
        op5 = getattr(instruction, 'arg5', None)
        op6 = getattr(instruction, 'arg6', None)

        if instruction.inst.name in ('Add', 'AddN', 'AddS'):
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT(' + '), RHRT(op3)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'Add32':
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        RT('__uasm.add32'),
                        LPT(),
                        RHRT(op2),
                        RT(', '),
                        RHRT(op3),
                        RPT(),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'AddEmptyString':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RT("'' + "), RHRT(op2)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'AsyncBreakCheck':
            lines.append(TS([], assembly=[instruction]))
        elif instruction.inst.name == 'BitAnd':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT(' & '), RHRT(op3)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'BitNot':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RT('~'), RHRT(op2)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'BitOr':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT(' | '), RHRT(op3)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'BitXor':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT(' ^ '), RHRT(op3)],
                    assembly=[instruction],
                )
            )
        # Note: It should be checked later whether the implementation of
        # parsing the "Call*" opcodes present below matches the difference
        # between the function_header.frameSize and the latest frame
        # register index across all version of the Hermes bytecode VM,
        # whether thisArg is handled correctly in all implementation of
        # the variants of the call, we should also eventually set up
        # unit tests, etc.
        elif instruction.inst.name in ('Call', 'CallLong'):
            args = []
            for register in reversed(
                range(
                    function_header.frameSize - 7 - op3,
                    function_header.frameSize - 7,
                )
            ):
                args += [RHRT(register), RT(', ')]
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        RHRT(function_header.frameSize - 7),
                        RT('['),
                        RHRT(op2),
                        RT(']'),
                        LPT(),
                        *args[:-1],
                        RPT(),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in ('Call1', 'Call2', 'Call3', 'Call4'):
            args = []
            for arg_count in range(1, int(instruction.inst.name[-1])):
                args += [RHRT([op4, op5, op6][arg_count - 1]), RT(', ')]
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        RHRT(op2),
                        BIND(op3),
                        LPT(),
                        *args[:-1],
                        RPT(),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in ('CallDirect', 'CallDirectLongIndex'):
            args = []
            for register in reversed(
                range(
                    function_header.frameSize - 7 - op2,
                    function_header.frameSize - 7,
                )
            ):
                args += [RHRT(register), RT(', ')]
            state.calldirect_function_ids.add(op3)
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        DAT(),
                        FTI(op3, state),
                        BIND(function_header.frameSize - 7),
                        LPT(),
                        *args[:-1],
                        RPT(),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in ('CallBuiltin', 'CallBuiltinLong'):
            args = []
            for register in reversed(
                range(
                    function_header.frameSize - 7 - (op3 - 1),
                    function_header.frameSize - 7,
                )
            ):
                args += [RHRT(register), RT(', ')]
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        FTI(op2, state, is_builtin=True),
                        LPT(),
                        *args[:-1],
                        RPT(),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'CallRequire':
            # CallRequire dest, env, module_id — cached require() call
            lines.append(
                TS(
                    [LHRT(op1), AT(), RT('require'), LPT(), RT(str(op3)), RPT()],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'CacheNewObject':
            lines.append(
                TS([LHRT(op1), AT(), RT('{}')], assembly=[instruction])
            )
        elif instruction.inst.name == 'Catch':
            lines.append(TS([CBS(op1)], assembly=[instruction]))
        elif instruction.inst.name == 'CoerceThisNS':
            lines.append(
                TS([LHRT(op1), AT(), RHRT(op2)], assembly=[instruction])
            )
        elif instruction.inst.name == 'CompleteGenerator':
            lines.append(TS([], assembly=[instruction]))
        elif instruction.inst.name in ('Construct', 'ConstructLong'):
            args = []
            for register in reversed(
                range(
                    function_header.frameSize - 7 - op3,
                    function_header.frameSize - 7,
                )
            ):
                args += [RHRT(register), RT(', ')]
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        RT('new '),
                        RHRT(function_header.frameSize - 7),
                        RT('['),
                        RHRT(op2),
                        RT(']'),
                        LPT(),
                        *args[:-1],
                        RPT(),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in (
            'CreateAsyncClosure',
            'CreateAsyncClosureLongIndex',
        ):
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        FTI(op3, state, op2 if op2 in _env_registers else None, is_async=True, is_closure=True),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in (
            'CreateClosure',
            'CreateClosureLongIndex',
        ):
            lines.append(
                TS(
                    [LHRT(op1), AT(), FTI(op3, state, op2 if op2 in _env_registers else None, is_closure=True)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'CreateEnvironment':
            # v97+: [Reg8(dest), Reg8(parent_env), UInt32(size)] — behaves like
            # pre-v97 CreateInnerEnvironment; pre-v97: [Reg8(dest)] only.
            if state.hbc_reader.header.version >= 97:
                lines.append(TS([NIET(op1, op2, op3)], assembly=[instruction]))
            else:
                lines.append(TS([NET(op1)], assembly=[instruction]))
        elif instruction.inst.name in (
            'CreateFunctionEnvironment',
            'CreateTopLevelEnvironment',
        ):
            lines.append(TS([NET(op1)], assembly=[instruction]))
        elif instruction.inst.name == 'CreateInnerEnvironment':
            lines.append(TS([NIET(op1, op2, op3)], assembly=[instruction]))
        elif instruction.inst.name in (
            'CreateGenerator',
            'CreateGeneratorLongIndex',
        ):
            lines.append(
                TS(
                    [LHRT(op1), AT(), FTI(op3, state, op2 if op2 in _env_registers else None, is_generator=True)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in (
            'CreateGeneratorClosure',
            'CreateGeneratorClosureLongIndex',
        ):
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        FTI(
                            op3, state, op2, is_closure=True, is_generator=True
                        ),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'CreatePrivateName':
            private_name = state.hbc_reader.strings[op2]
            lines.append(
                TS(
                    [LHRT(op1), AT(), RT('Symbol'), LPT(), RT(repr(private_name)), RPT()],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'CreateRegExp':
            pattern_string = state.hbc_reader.strings[op2]
            flags_string = state.hbc_reader.strings[op3]

            pattern_string = pattern_string.translate(
                {char: repr(char) for char in range(0x20)}
            )
            #   pattern_string = pattern_string.replace('/', '\\/')

            readable_regexp = '/%s/%s' % (pattern_string, flags_string)

            lines.append(
                TS(
                    [LHRT(op1), AT(), RT(readable_regexp)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'CreateThis':
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        RT('Object.create'),
                        LPT(),
                        RHRT(op2),
                        RT(', {constructor: {value: '),
                        RHRT(op3),
                        RT('}}'),
                        RPT(),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in ('CreateThisForNew', 'CreateThisForSuper'):
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        RT('Object.create'),
                        LPT(),
                        RHRT(op2),
                        DAT(),
                        RT('prototype'),
                        RPT(),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'Debugger':
            lines.append(TS([RT('debugger')], assembly=[instruction]))
        elif instruction.inst.name == 'DebuggerBreakCheck':
            lines.append(TS([], assembly=[instruction]))
        elif instruction.inst.name == 'Dec':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT(' - 1')],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'DeclareGlobalVar':
            global_var = state.hbc_reader.strings[op1]

            lines.append(
                TS(
                    [RT(global_var), AT(), RT('undefined')],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in (
            'DelById',
            'DelByIdLong',
            'DelByIdLoose',
            'DelByIdLooseLong',
            'DelByIdStrict',
            'DelByIdStrictLong',
        ):
            prop_string = state.hbc_reader.strings[op3]

            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        RT('delete '),
                        RHRT(op2),
                        DAT(),
                        RT(prop_string),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in (
            'DelByVal',
            'DelByValLoose',
            'DelByValStrict',
        ):
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        RT('delete '),
                        RHRT(op2),
                        RT('['),
                        RHRT(op3),
                        RT(']'),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'DirectEval':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RT('eval'), LPT(), RHRT(op2), RPT()],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in ('Div', 'DivN'):
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT(' / '), RHRT(op3)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'Divi32':
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        RT('__uasm.divi32'),
                        LPT(),
                        RHRT(op2),
                        RT(', '),
                        RHRT(op3),
                        RPT(),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'Divu32':
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        RT('__uasm.divu32'),
                        LPT(),
                        RHRT(op2),
                        RT(', '),
                        RHRT(op3),
                        RPT(),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'Eq':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT(' == '), RHRT(op3)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'GetArgumentsLength':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RT('arguments.length')],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in (
            'GetArgumentsPropByVal',
            'GetArgumentsPropByValLoose',
            'GetArgumentsPropByValStrict',
        ):
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        RT('arguments'),
                        RT('['),
                        RHRT(op2),
                        RT(']'),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'GetBuiltinClosure':
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        FTI(op2, state, is_builtin=True, is_closure=True),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in (
            'GetById',
            'GetByIdLong',
            'GetByIdShort',
            'TryGetById',
            'TryGetByIdLong',
        ):
            string = state.hbc_reader.strings[op4]

            if ' ' in string or invalid_js_property.match(string):
                lines.append(
                    TS(
                        [LHRT(op1), AT(), RHRT(op2), IST(string)],
                        assembly=[instruction],
                    )
                )
            else:
                lines.append(
                    TS(
                        [LHRT(op1), AT(), RHRT(op2), DAT(), RT(string)],
                        assembly=[instruction],
                    )
                )
        elif instruction.inst.name in ('GetByIdWithReceiverLong',):
            string = state.hbc_reader.strings[op5]

            if ' ' in string or invalid_js_property.match(string):
                lines.append(
                    TS(
                        [LHRT(op1), AT(), RHRT(op2), IST(string)],
                        assembly=[instruction],
                    )
                )
            else:
                lines.append(
                    TS(
                        [LHRT(op1), AT(), RHRT(op2), DAT(), RT(string)],
                        assembly=[instruction],
                    )
                )

        elif instruction.inst.name == 'FastArrayLength':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), DAT(), RT('length')],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'FastArrayPush':
            lines.append(
                TS(
                    [
                        RHRT(op1),
                        DAT(),
                        RT('push'),
                        LPT(),
                        RHRT(op2),
                        RPT(),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'FastArrayAppend':
            lines.append(
                TS(
                    [
                        RT('Array.prototype.push.apply'),
                        LPT(),
                        RHRT(op1),
                        RT(', '),
                        RHRT(op2),
                        RPT(),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in (
            'GetByVal',
            'GetByValWithReceiver',
            'FastArrayLoad',
            'GetByIndex',
            'GetOwnBySlotIdx',
            'GetOwnBySlotIdxLong',
        ):
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT('['), RHRT(op3), RT(']')],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'GetOwnPrivateBySym':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT('['), RHRT(op4), RT(']')],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'GetClosureEnvironment':
            lines.append(TS([GET(op1, 0)], assembly=[instruction]))
        elif instruction.inst.name == 'GetEnvironment':
            if state.hbc_reader.header.version < 97:
                lines.append(TS([GET(op1, op2)], assembly=[instruction]))
            else:
                lines.append(TS([GET(op1, op3)], assembly=[instruction]))
        elif instruction.inst.name == 'GetParentEnvironment':
            lines.append(TS([GET(op1, op2)], assembly=[instruction]))
        elif instruction.inst.name == 'GetGlobalObject':
            lines.append(
                TS([LHRT(op1), AT(), RT('global')], assembly=[instruction])
            )
        elif instruction.inst.name == 'GetNewTarget':
            lines.append(
                TS([LHRT(op1), AT(), RT('new.target')], assembly=[instruction])
            )
        elif instruction.inst.name == 'GetNextPName':
            lines.append(
                TS([FILNI(op1, op2, op3, op4, op5)], assembly=[instruction])
            )
        elif instruction.inst.name == 'GetPNameList':
            lines.append(
                TS([FILI(op1, op2, op3, op4)], assembly=[instruction])
            )
        elif instruction.inst.name == 'Greater':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT(' > '), RHRT(op3)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'GreaterEq':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT(' >= '), RHRT(op3)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'Inc':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT(' + 1')],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'InstanceOf':
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        RHRT(op2),
                        RT(' instanceof '),
                        RHRT(op3),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in ('IsIn', 'PrivateIsIn'):
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT(' in '), RHRT(op3)],
                    assembly=[instruction],
                )
            )
        # Note: The implementations of the methods related to the iteration below
        # is not fully consistent with the corresponding React Native instruction
        # behavior, which has special handling for iterating over arrays, may
        # suppress propagating the exception over certain IteratorClose() calls...
        #
        # This may be improved in the future if any required.
        elif instruction.inst.name == 'IteratorBegin':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT('[Symbol.iterator]')],
                    assembly=[instruction],
                )
            )
            lines.append(
                TS(
                    [
                        LHRT(op2),
                        AT(),
                        RHRT(op1),
                        LPT(),
                        RPT(),
                        DAT(),
                        RT('next'),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'IteratorNext':
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        RHRT(op3),
                        LPT(),
                        RPT(),
                        DAT(),
                        RT('value'),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'IteratorClose':
            lines.append(
                TS(
                    [RHRT(op1), DAT(), RT('return'), LPT(), RPT()],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in ('JEqual', 'JEqualLong'):
            if op1 > 0:
                lines.append(
                    TS(
                        [
                            JNC(instruction.original_pos + op1),
                            RHRT(op2),
                            RT(' != '),
                            RHRT(op3),
                        ],
                        assembly=[instruction],
                    )
                )
            else:
                lines.append(
                    TS(
                        [
                            JC(instruction.original_pos + op1),
                            RHRT(op2),
                            RT(' == '),
                            RHRT(op3),
                        ],
                        assembly=[instruction],
                    )
                )
        elif instruction.inst.name in ('JmpBuiltinIs', 'JmpBuiltinIsLong'):
            if op1 > 0:
                lines.append(
                    TS(
                        [JNC(instruction.original_pos + op1), RT('!'), RHRT(op3)],
                        assembly=[instruction],
                    )
                )
            else:
                lines.append(
                    TS(
                        [JC(instruction.original_pos + op1), RHRT(op3)],
                        assembly=[instruction],
                    )
                )
        elif instruction.inst.name in ('JmpBuiltinIsNot', 'JmpBuiltinIsNotLong'):
            if op1 > 0:
                lines.append(
                    TS(
                        [JNC(instruction.original_pos + op1), RHRT(op3)],
                        assembly=[instruction],
                    )
                )
            else:
                lines.append(
                    TS(
                        [JC(instruction.original_pos + op1), RT('!'), RHRT(op3)],
                        assembly=[instruction],
                    )
                )
        elif instruction.inst.name == 'JmpTypeOfIs':
            target = instruction.original_pos + op1
            if op1 > 0:
                # JNC renders if(!C) jump; use complement bitmask so that
                # if(!C) = if(original match) when the tokens are negated
                lines.append(
                    TS(
                        [JNC(target)] + _typeof_cond_tokens(511 ^ op3, op2),
                        assembly=[instruction],
                    )
                )
            else:
                lines.append(
                    TS(
                        [JC(target)] + _typeof_cond_tokens(op3, op2),
                        assembly=[instruction],
                    )
                )
        elif instruction.inst.name in (
            'JGreater',
            'JGreaterN',
            'JGreaterLong',
            'JGreaterNLong',
        ):
            if op1 > 0:
                lines.append(
                    TS(
                        [
                            JNC(instruction.original_pos + op1),
                            RT('!'),
                            LPT(),
                            RHRT(op2),
                            RT(' > '),
                            RHRT(op3),
                            RPT(),
                        ],
                        assembly=[instruction],
                    )
                )
            else:
                lines.append(
                    TS(
                        [
                            JC(instruction.original_pos + op1),
                            RHRT(op2),
                            RT(' > '),
                            RHRT(op3),
                        ],
                        assembly=[instruction],
                    )
                )
        elif instruction.inst.name in (
            'JNotGreater',
            'JNotGreaterN',
            'JNotGreaterLong',
            'JNotGreaterNLong',
        ):
            if op1 > 0:
                lines.append(
                    TS(
                        [
                            JNC(instruction.original_pos + op1),
                            RHRT(op2),
                            RT(' > '),
                            RHRT(op3),
                        ],
                        assembly=[instruction],
                    )
                )
            else:
                lines.append(
                    TS(
                        [
                            JC(instruction.original_pos + op1),
                            RT('!'),
                            LPT(),
                            RHRT(op2),
                            RT(' > '),
                            RHRT(op3),
                            RPT(),
                        ],
                        assembly=[instruction],
                    )
                )
        elif instruction.inst.name in (
            'JGreaterEqual',
            'JGreaterEqualN',
            'JGreaterEqualLong',
            'JGreaterEqualNLong',
        ):
            if op1 > 0:
                lines.append(
                    TS(
                        [
                            JNC(instruction.original_pos + op1),
                            RT('!'),
                            LPT(),
                            RHRT(op2),
                            RT(' >= '),
                            RHRT(op3),
                            RPT(),
                        ],
                        assembly=[instruction],
                    )
                )
            else:
                lines.append(
                    TS(
                        [
                            JC(instruction.original_pos + op1),
                            RHRT(op2),
                            RT(' >= '),
                            RHRT(op3),
                        ],
                        assembly=[instruction],
                    )
                )
        elif instruction.inst.name in (
            'JNotGreaterEqual',
            'JNotGreaterEqualN',
            'JNotGreaterEqualLong',
            'JNotGreaterEqualNLong',
        ):
            if op1 > 0:
                lines.append(
                    TS(
                        [
                            JNC(instruction.original_pos + op1),
                            RHRT(op2),
                            RT(' >= '),
                            RHRT(op3),
                        ],
                        assembly=[instruction],
                    )
                )
            else:
                lines.append(
                    TS(
                        [
                            JC(instruction.original_pos + op1),
                            RT('!'),
                            LPT(),
                            RHRT(op2),
                            RT(' >= '),
                            RHRT(op3),
                            RPT(),
                        ],
                        assembly=[instruction],
                    )
                )
        elif instruction.inst.name in (
            'JLess',
            'JLessN',
            'JLessLong',
            'JLessNLong',
        ):
            if op1 > 0:
                lines.append(
                    TS(
                        [
                            JNC(instruction.original_pos + op1),
                            RT('!'),
                            LPT(),
                            RHRT(op2),
                            RT(' < '),
                            RHRT(op3),
                            RPT(),
                        ],
                        assembly=[instruction],
                    )
                )
            else:
                lines.append(
                    TS(
                        [
                            JC(instruction.original_pos + op1),
                            RHRT(op2),
                            RT(' < '),
                            RHRT(op3),
                        ],
                        assembly=[instruction],
                    )
                )
        elif instruction.inst.name in (
            'JNotLess',
            'JNotLessN',
            'JNotLessLong',
            'JNotLessNLong',
        ):
            if op1 > 0:
                lines.append(
                    TS(
                        [
                            JNC(instruction.original_pos + op1),
                            RHRT(op2),
                            RT(' < '),
                            RHRT(op3),
                        ],
                        assembly=[instruction],
                    )
                )
            else:
                lines.append(
                    TS(
                        [
                            JC(instruction.original_pos + op1),
                            RT('!'),
                            LPT(),
                            RHRT(op2),
                            RT(' < '),
                            RHRT(op3),
                            RPT(),
                        ],
                        assembly=[instruction],
                    )
                )
        elif instruction.inst.name in (
            'JLessEqual',
            'JLessEqualN',
            'JLessEqualLong',
            'JLessEqualNLong',
        ):
            if op1 > 0:
                lines.append(
                    TS(
                        [
                            JNC(instruction.original_pos + op1),
                            RT('!'),
                            LPT(),
                            RHRT(op2),
                            RT(' <= '),
                            RHRT(op3),
                            RPT(),
                        ],
                        assembly=[instruction],
                    )
                )
            else:
                lines.append(
                    TS(
                        [
                            JC(instruction.original_pos + op1),
                            RHRT(op2),
                            RT(' <= '),
                            RHRT(op3),
                        ],
                        assembly=[instruction],
                    )
                )
        elif instruction.inst.name in (
            'JNotLessEqual',
            'JNotLessEqualN',
            'JNotLessEqualLong',
            'JNotLessEqualNLong',
        ):
            if op1 > 0:
                lines.append(
                    TS(
                        [
                            JNC(instruction.original_pos + op1),
                            RHRT(op2),
                            RT(' <= '),
                            RHRT(op3),
                        ],
                        assembly=[instruction],
                    )
                )
            else:
                lines.append(
                    TS(
                        [
                            JC(instruction.original_pos + op1),
                            RT('!'),
                            LPT(),
                            RHRT(op2),
                            RT(' <= '),
                            RHRT(op3),
                            RPT(),
                        ],
                        assembly=[instruction],
                    )
                )
        elif instruction.inst.name in ('JNotEqual', 'JNotEqualLong'):
            if op1 > 0:
                lines.append(
                    TS(
                        [
                            JNC(instruction.original_pos + op1),
                            RHRT(op2),
                            RT(' == '),
                            RHRT(op3),
                        ],
                        assembly=[instruction],
                    )
                )
            else:
                lines.append(
                    TS(
                        [
                            JC(instruction.original_pos + op1),
                            RHRT(op2),
                            RT(' != '),
                            RHRT(op3),
                        ],
                        assembly=[instruction],
                    )
                )
        elif instruction.inst.name in ('JStrictEqual', 'JStrictEqualLong'):
            if op1 > 0:
                lines.append(
                    TS(
                        [
                            JNC(instruction.original_pos + op1),
                            RHRT(op2),
                            RT(' !== '),
                            RHRT(op3),
                        ],
                        assembly=[instruction],
                    )
                )
            else:
                lines.append(
                    TS(
                        [
                            JC(instruction.original_pos + op1),
                            RHRT(op2),
                            RT(' === '),
                            RHRT(op3),
                        ],
                        assembly=[instruction],
                    )
                )
        elif instruction.inst.name in (
            'JStrictNotEqual',
            'JStrictNotEqualLong',
        ):
            if op1 > 0:
                lines.append(
                    TS(
                        [
                            JNC(instruction.original_pos + op1),
                            RHRT(op2),
                            RT(' === '),
                            RHRT(op3),
                        ],
                        assembly=[instruction],
                    )
                )
            else:
                lines.append(
                    TS(
                        [
                            JC(instruction.original_pos + op1),
                            RHRT(op2),
                            RT(' !== '),
                            RHRT(op3),
                        ],
                        assembly=[instruction],
                    )
                )
        elif instruction.inst.name in ('Jmp', 'JmpLong'):
            if op1 > 0:
                lines.append(
                    TS(
                        [JNC(instruction.original_pos + op1), RT('false')],
                        assembly=[instruction],
                    )
                )
            else:
                lines.append(
                    TS(
                        [JC(instruction.original_pos + op1), RT('true')],
                        assembly=[instruction],
                    )
                )
        elif instruction.inst.name in ('JmpFalse', 'JmpFalseLong'):
            if op1 > 0:
                lines.append(
                    TS(
                        [JNC(instruction.original_pos + op1), RHRT(op2)],
                        assembly=[instruction],
                    )
                )
            else:
                lines.append(
                    TS(
                        [
                            JC(instruction.original_pos + op1),
                            RT('!'),
                            RHRT(op2),
                        ],
                        assembly=[instruction],
                    )
                )
        elif instruction.inst.name in ('JmpTrue', 'JmpTrueLong'):
            if op1 > 0:
                lines.append(
                    TS(
                        [
                            JNC(instruction.original_pos + op1),
                            RT('!'),
                            RHRT(op2),
                        ],
                        assembly=[instruction],
                    )
                )
            else:
                lines.append(
                    TS(
                        [JC(instruction.original_pos + op1), RHRT(op2)],
                        assembly=[instruction],
                    )
                )
        elif instruction.inst.name in ('JmpUndefined', 'JmpUndefinedLong'):
            if op1 > 0:
                lines.append(
                    TS(
                        [
                            JNC(instruction.original_pos + op1),
                            RHRT(op2),
                            RT(' !== undefined'),
                        ],
                        assembly=[instruction],
                    )
                )
            else:
                lines.append(
                    TS(
                        [
                            JC(instruction.original_pos + op1),
                            RHRT(op2),
                            RT(' === undefined'),
                        ],
                        assembly=[instruction],
                    )
                )
        elif instruction.inst.name == 'LShift':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT(' << '), RHRT(op3)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'Less':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT(' < '), RHRT(op3)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'LessEq':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT(' <= '), RHRT(op3)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in (
            'LoadConstBigInt',
            'LoadConstBigIntLongIndex',
        ):
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        RT(str(state.hbc_reader.bigint_values[op2]) + 'n'),
                    ],
                    assembly=[instruction],
                )
            )  # TODO : Decode BigInts correctly
        elif instruction.inst.name in (
            'LoadConstDouble',
            'LoadConstInt',
            'LoadConstUInt8',
        ):
            lines.append(
                TS([LHRT(op1), AT(), str(op2)], assembly=[instruction])
            )
        elif instruction.inst.name in ('LoadConstEmpty', 'LoadConstUndefined'):
            lines.append(
                TS([LHRT(op1), AT(), RT('undefined')], assembly=[instruction])
            )
        elif instruction.inst.name == 'LoadConstFalse':
            lines.append(
                TS([LHRT(op1), AT(), RT('false')], assembly=[instruction])
            )
        elif instruction.inst.name == 'LoadConstNull':
            lines.append(
                TS([LHRT(op1), AT(), RT('null')], assembly=[instruction])
            )
        elif instruction.inst.name in (
            'LoadConstString',
            'LoadConstStringLongIndex',
        ):
            lines.append(
                TS(
                    [LHRT(op1), AT(), RT(repr(state.hbc_reader.strings[op2]))],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'LoadConstTrue':
            lines.append(
                TS([LHRT(op1), AT(), RT('true')], assembly=[instruction])
            )
        elif instruction.inst.name == 'LoadConstZero':
            lines.append(
                TS([LHRT(op1), AT(), RT('0')], assembly=[instruction])
            )
        elif instruction.inst.name in (
            'LoadFromEnvironment',
            'LoadFromEnvironmentL',
        ):
            lines.append(
                TS([LHRT(op1), AT(), LFET(op2, op3)], assembly=[instruction])
            )
        elif instruction.inst.name in ('LoadParam', 'LoadParamLong'):
            if not op2:
                arg_name = 'this'
            elif op2 < function_body.function_object.paramCount:
                arg_name = 'a' + str(op2 - 1)
            else:
                arg_name = 'arguments[%d]' % (op2 - 1)
            lines.append(
                TS([LHRT(op1), AT(), RT(arg_name)], assembly=[instruction])
            )
        elif instruction.inst.name == 'LoadThisNS':
            lines.append(
                TS([LHRT(op1), AT(), RT('this')], assembly=[instruction])
            )
        elif instruction.inst.name in ('LoadParentNoTraps', 'TypedLoadParent'):
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), DAT(), RT('__proto__')],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in (
            'Loadi16',
            'Loadi32',
            'Loadi8',
            'Loadu16',
            'Loadu32',
            'Loadu8',
        ):
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        RT('__uasm.' + instruction.inst.name.lower()),
                        LPT(),
                        RHRT(op2),
                        RT(', '),
                        RHRT(op3),
                        RPT(),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'Mod':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT(' % '), RHRT(op3)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in ('Mov', 'MovLong'):
            lines.append(
                TS([LHRT(op1), AT(), RHRT(op2)], assembly=[instruction])
            )
        elif instruction.inst.name == 'Mul32':
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        RT('__uasm.mul32'),
                        LPT(),
                        RHRT(op2),
                        RT(', '),
                        RHRT(op3),
                        RPT(),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in ('Mul', 'MulN'):
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT(' * '), RHRT(op3)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'Negate':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RT('-'), RHRT(op2)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'Neq':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT(' != '), RHRT(op3)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'NewArray':
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        RT('new Array'),
                        LPT(),
                        RT(str(op2)),
                        RPT(),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in (
            'NewArrayWithBuffer',
            'NewArrayWithBufferLong',
        ):
            array_text = '[%s]' % ', '.join(
                unpack_slp_array(
                    (
                        state.hbc_reader.arrays
                        if state.hbc_reader.header.version < 97
                        else state.hbc_reader.literal_values
                    )[op4:],
                    op3,
                ).to_strings(state.hbc_reader.strings)
            )
            lines.append(
                TS([LHRT(op1), AT(), RT(array_text)], assembly=[instruction])
            )
        elif instruction.inst.name == 'NewObject':
            lines.append(
                TS([LHRT(op1), AT(), RT('{}')], assembly=[instruction])
            )
        elif instruction.inst.name in (
            'NewObjectWithBuffer',
            'NewObjectWithBufferLong',
        ):
            if state.hbc_reader.header.version < 97:
                object_text = '{%s}' % ', '.join(
                    '%s: %s' % (key, value)
                    for key, value in zip(
                        unpack_slp_array(
                            state.hbc_reader.object_keys[op4:], op3
                        ).to_strings(state.hbc_reader.strings),
                        unpack_slp_array(
                            (state.hbc_reader.object_values)[op5:],
                            op3,
                        ).to_strings(state.hbc_reader.strings),
                    )
                )
            else:
                shape_keys = state.hbc_reader.object_shape_keys[op2]
                object_text = '{%s}' % ', '.join(
                    '%s: %s' % (key, value)
                    for key, value in zip(
                        shape_keys,
                        unpack_slp_array(
                            (state.hbc_reader.literal_values)[op3:],
                            len(shape_keys),
                        ).to_strings(state.hbc_reader.strings),
                    )
                )
            lines.append(
                TS([LHRT(op1), AT(), RT(object_text)], assembly=[instruction])
            )
        elif instruction.inst.name == 'NewObjectWithBufferAndParent':
            shape_keys = state.hbc_reader.object_shape_keys[op3]
            object_text = '{%s}' % ', '.join(
                '%s: %s' % (key, value)
                for key, value in zip(
                    shape_keys,
                    unpack_slp_array(
                        state.hbc_reader.literal_values[op4:],
                        len(shape_keys),
                    ).to_strings(state.hbc_reader.strings),
                )
            )
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        RT('Object.assign'),
                        LPT(),
                        RT('Object.create'),
                        LPT(),
                        RHRT(op2),
                        RPT(),
                        RT(', '),
                        RT(object_text),
                        RPT(),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'NewTypedObjectWithBuffer':
            # Same layout as NewObjectWithBufferAndParent + a UInt8 type-id (op5)
            shape_keys = state.hbc_reader.object_shape_keys[op3]
            object_text = '{%s}' % ', '.join(
                '%s: %s' % (key, value)
                for key, value in zip(
                    shape_keys,
                    unpack_slp_array(
                        state.hbc_reader.literal_values[op4:],
                        len(shape_keys),
                    ).to_strings(state.hbc_reader.strings),
                )
            )
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        RT('Object.assign'),
                        LPT(),
                        RT('Object.create'),
                        LPT(),
                        RHRT(op2),
                        RPT(),
                        RT(', '),
                        RT(object_text),
                        RPT(),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'NewObjectWithParent':
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        RT('Object.create'),
                        LPT(),
                        RHRT(op2),
                        RPT(),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'Not':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RT('!'), RHRT(op2)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'ProfilePoint':
            lines.append(TS([], assembly=[instruction]))
        elif instruction.inst.name in (
            'PutById',
            'PutByIdLong',
            'PutByIdLoose',
            'PutByIdLooseLong',
            'PutByIdStrict',
            'PutByIdStrictLong',
            'DefineOwnById',
            'DefineOwnByIdLong',
            'TryPutById',
            'TryPutByIdLong',
            'TryPutByIdLoose',
            'TryPutByIdLooseLong',
            'TryPutByIdStrict',
            'TryPutByIdStrictLong',
        ):
            index = repr(state.hbc_reader.strings[op4])
            lines.append(
                TS(
                    [LHRT(op1), RT('[' + index + ']'), AT(), RHRT(op2)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in (
            'PutNewOwnById',
            'PutNewOwnByIdLong',
            'PutNewOwnByIdShort',
        ):
            index = repr(state.hbc_reader.strings[op3])
            lines.append(
                TS(
                    [LHRT(op1), RT('[' + index + ']'), AT(), RHRT(op2)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in (
            'PutNewOwnNEById',
            'PutNewOwnNEByIdLong',
        ):
            index = repr(state.hbc_reader.strings[op3])
            lines.append(
                TS(
                    [
                        RT('Object.defineProperty'),
                        LPT(),
                        LHRT(op1),
                        RT(', '),
                        RT(repr(index)),
                        RT(', {value: '),
                        RHRT(op2),
                        RT('}'),
                        RPT(),
                    ],
                    assembly=[instruction],
                )
            )
            # TODO: Are non-enumerable values set correctly?
            # When are these used if they are used?
        elif instruction.inst.name in (
            'PutByVal',
            'PutByValLoose',
            'PutByValStrict',
            'PutByValWithReceiver',
            'AddOwnPrivateBySym',
            'FastArrayStore',
        ):
            lines.append(
                TS(
                    [LHRT(op1), RT('['), RHRT(op2), RT(']'), AT(), RHRT(op3)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'PutOwnPrivateBySym':
            lines.append(
                TS(
                    [LHRT(op1), RT('['), RHRT(op4), RT(']'), AT(), RHRT(op2)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in (
            'PutOwnByIndex',
            'PutOwnByIndexL',
            'PutOwnBySlotIdx',
            'PutOwnBySlotIdxLong',
            'PutOwnByVal',
            'DefineOwnByIndex',
            'DefineOwnByIndexL',
            'DefineOwnByVal',
            'DefineOwnInDenseArray',
            'DefineOwnInDenseArrayL',
        ):
            lines.append(
                TS(
                    [LHRT(op1), RT('[%d]' % op3), AT(), RHRT(op2)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in (
            'PutOwnGetterSetterByVal',
            'DefineOwnGetterSetterByVal',
        ):
            index = repr(state.hbc_reader.strings[op3])
            lines.append(
                TS(
                    [
                        RT('Object.defineProperty'),
                        LPT(),
                        LHRT(op1),
                        RT(', '),
                        RHRT(op2),
                        RT(', {get: '),
                        RHRT(op3),
                        RT(', set: '),
                        RHRT(op4),
                        RT(
                            ', enumerable: '
                            + ('true' if op5 else 'false')
                            + '}'
                        ),
                        RPT(),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'RShift':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT(' >> '), RHRT(op3)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in (
            'ReifyArguments',
            'ReifyArgumentsLoose',
            'ReifyArgumentsStrict',
        ):
            lines.append(
                TS([LHRT(op1), AT(), RT('arguments')], assembly=[instruction])
            )
        elif instruction.inst.name == 'ResumeGenerator':
            lines.append(TS([RG(op1, op2)], assembly=[instruction]))
        elif instruction.inst.name == 'Ret':
            lines.append(TS([RD(), RHRT(op1)], assembly=[instruction]))
        elif instruction.inst.name in ('SaveGenerator', 'SaveGeneratorLong'):
            lines.append(
                TS(
                    [SG(instruction.original_pos + op1)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'SelectObject':
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        RHRT(op3),
                        RT(' instanceof Object ? '),
                        RHRT(op3),
                        RT(' : '),
                        RHRT(op2),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'StartGenerator':
            lines.append(TS([SG2()], assembly=[instruction]))
        elif instruction.inst.name in ('Store16', 'Store32', 'Store8'):
            lines.append(
                TS(
                    [
                        RT('__uasm.' + instruction.inst.name.lower()),
                        LPT(),
                        RHRT(op1),
                        RT(', '),
                        RHRT(op2),
                        RT(', '),
                        RHRT(op3),
                        RPT(),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in (
            'StoreNPToEnvironment',
            'StoreNPToEnvironmentL',
            'StoreToEnvironment',
            'StoreToEnvironmentL',
        ):
            lines.append(TS([STE(op1, op2, op3)], assembly=[instruction]))
        elif instruction.inst.name == 'StrictEq':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT(' === '), RHRT(op3)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'StrictNeq':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT(' !== '), RHRT(op3)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in ('Sub', 'SubN'):
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT(' - '), RHRT(op3)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'Sub32':
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        RT('__uasm.sub32'),
                        LPT(),
                        RHRT(op2),
                        RT(', '),
                        RHRT(op3),
                        RPT(),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name in ('SwitchImm', 'UIntSwitchImm'):
            lines.append(
                TS(
                    [
                        SI(
                            op1,
                            instruction.original_pos + op2,
                            instruction.original_pos + op3,
                            op4,
                            op5,
                        ),
                        RT(
                            ' // Switch table: %s'
                            % instruction.switch_jump_table
                        ),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'StringSwitchImm':
            lines.append(
                TS(
                    [
                        RT(
                            '// StringSwitchImm: switch(%s) { default: goto %d }'
                            % (
                                'r%d' % op1,
                                instruction.original_pos + op4,
                            )
                        )
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'Throw':
            lines.append(TS([TD(), RHRT(op1)], assembly=[instruction]))
        elif instruction.inst.name == 'ThrowIfEmpty':
            lines.append(
                TS(
                    [
                        RT('if'),
                        LPT(),
                        RT('!'),
                        RHRT(op2),
                        RPT(),
                        RT(' '),
                        TD(),
                        RT(
                            'ReferenceError("accessing an uninitialized variable")'
                        ),
                    ],
                    assembly=[instruction],
                )
            )
            lines.append(
                TS([RT('else '), LHRT(op1), AT(), RHRT(op2)], assembly=[])
            )
        elif instruction.inst.name == 'ThrowIfThisInitialized':
            lines.append(
                TS(
                    [
                        RT('if'),
                        LPT(),
                        RHRT(op1),
                        RPT(),
                        RT(' '),
                        TD(),
                        RT('ReferenceError("\'super()\' already called")'),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'ThrowIfUndefined':
            lines.append(
                TS(
                    [
                        RT('if'),
                        LPT(),
                        RHRT(op2),
                        RT(' === undefined'),
                        RPT(),
                        RT(' '),
                        TD(),
                        RT(
                            'ReferenceError("accessing an uninitialized variable")'
                        ),
                    ],
                    assembly=[instruction],
                )
            )
            lines.append(
                TS([LHRT(op1), AT(), RHRT(op2)], assembly=[])
            )
        elif instruction.inst.name == 'ThrowIfHasRestrictedGlobalProperty':
            global_var = state.hbc_reader.strings[op1]

            lines.append(
                TS(
                    [
                        RT('if'),
                        LPT(),
                        RT('typeof global'),
                        DAT(),
                        RT(global_var),
                        RT(" === 'undefined'"),
                        RPT(),
                        RT(' '),
                        TD(),
                        RT(
                            'SyntaxError("Name is a restricted global identifier")'
                        ),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'ThrowIfUndefinedInst':
            lines.append(
                TS(
                    [
                        RT('if'),
                        LPT(),
                        RT('typeof '),
                        RHRT(op1),
                        RT(" === 'undefined'"),
                        RPT(),
                        RT(' '),
                        TD(),
                        RT(
                            'ReferenceError("accessing an uninitialized variable")'
                        ),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'ToInt32':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT(' | 0')],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'ToPropertyKey':
            lines.append(
                TS([LHRT(op1), AT(), RHRT(op2)], assembly=[instruction])
            )
        elif instruction.inst.name == 'ToUint32':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT(' >>> 0')],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'ToNumber':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT(' - 0')],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'ToNumeric':
            lines.append(
                TS(
                    [
                        LHRT(op1),
                        AT(),
                        RT('parseFloat'),
                        LPT(),
                        RHRT(op2),
                        RPT(),
                    ],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'TypeOf':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RT('typeof '), RHRT(op2)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'TypeOfIs':
            lines.append(
                TS(
                    [LHRT(op1), AT()] + _typeof_cond_tokens(op3, op2),
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'URshift':
            lines.append(
                TS(
                    [LHRT(op1), AT(), RHRT(op2), RT(' >>> '), RHRT(op3)],
                    assembly=[instruction],
                )
            )
        elif instruction.inst.name == 'Unreachable':
            lines.append(
                TS(
                    [RT('// Unreachable position reached: %r' % instruction)],
                    assembly=[instruction],
                )
            )

        else:
            lines.append(
                TS(
                    [RT('// Unsupported instruction: %r' % instruction)],
                    assembly=[instruction],
                )
            )
            """
            # Todo: We should likely put an "Error comment" in the decompiled
            # source later, instead of this
            raise NotImplementedError('[Unsupported instruction in function "%s":] %r' % (
                function_body.function_name,
                instruction
            ))
            """
