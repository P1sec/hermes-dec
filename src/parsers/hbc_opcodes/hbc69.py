#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
"""
    Note: The contents of the current file have been automatically
    generated by the "utils/hermes_bytecode_structs_parser.py"
    script
    
    Please do not edit it manually. 👍
"""

from typing import List, Set, Dict, Union, Optional, Sequence, Any

# Imports from the current diretory
from .def_classes import *

_instructions : List[Instruction] = []

Reg8 = OperandType('Reg8', 'uint8_t')
Reg32 = OperandType('Reg32', 'uint32_t')
UInt8 = OperandType('UInt8', 'uint8_t')
UInt16 = OperandType('UInt16', 'uint16_t')
UInt32 = OperandType('UInt32', 'uint32_t')
Addr8 = OperandType('Addr8', 'int8_t')
Addr32 = OperandType('Addr32', 'int32_t')
Imm32 = OperandType('Imm32', 'int32_t')
Double = OperandType('Double', 'double')

NewObjectWithBuffer = Instruction('NewObjectWithBuffer', 0, [Reg8, UInt16, UInt16, UInt16, UInt16], globals())

NewObjectWithBufferLong = Instruction('NewObjectWithBufferLong', 1, [Reg8, UInt16, UInt16, UInt32, UInt32], globals())

NewObject = Instruction('NewObject', 2, [Reg8], globals())

NewObjectWithParent = Instruction('NewObjectWithParent', 3, [Reg8, Reg8], globals())

NewArrayWithBuffer = Instruction('NewArrayWithBuffer', 4, [Reg8, UInt16, UInt16, UInt16], globals())

NewArrayWithBufferLong = Instruction('NewArrayWithBufferLong', 5, [Reg8, UInt16, UInt16, UInt32], globals())

NewArray = Instruction('NewArray', 6, [Reg8, UInt16], globals())

Mov = Instruction('Mov', 7, [Reg8, Reg8], globals())

MovLong = Instruction('MovLong', 8, [Reg32, Reg32], globals())

Negate = Instruction('Negate', 9, [Reg8, Reg8], globals())

Not = Instruction('Not', 10, [Reg8, Reg8], globals())

BitNot = Instruction('BitNot', 11, [Reg8, Reg8], globals())

TypeOf = Instruction('TypeOf', 12, [Reg8, Reg8], globals())

Eq = Instruction('Eq', 13, [Reg8, Reg8, Reg8], globals())

StrictEq = Instruction('StrictEq', 14, [Reg8, Reg8, Reg8], globals())

Neq = Instruction('Neq', 15, [Reg8, Reg8, Reg8], globals())

StrictNeq = Instruction('StrictNeq', 16, [Reg8, Reg8, Reg8], globals())

Less = Instruction('Less', 17, [Reg8, Reg8, Reg8], globals())

LessEq = Instruction('LessEq', 18, [Reg8, Reg8, Reg8], globals())

Greater = Instruction('Greater', 19, [Reg8, Reg8, Reg8], globals())

GreaterEq = Instruction('GreaterEq', 20, [Reg8, Reg8, Reg8], globals())

Add = Instruction('Add', 21, [Reg8, Reg8, Reg8], globals())

AddN = Instruction('AddN', 22, [Reg8, Reg8, Reg8], globals())

Mul = Instruction('Mul', 23, [Reg8, Reg8, Reg8], globals())

MulN = Instruction('MulN', 24, [Reg8, Reg8, Reg8], globals())

Div = Instruction('Div', 25, [Reg8, Reg8, Reg8], globals())

DivN = Instruction('DivN', 26, [Reg8, Reg8, Reg8], globals())

Mod = Instruction('Mod', 27, [Reg8, Reg8, Reg8], globals())

Sub = Instruction('Sub', 28, [Reg8, Reg8, Reg8], globals())

SubN = Instruction('SubN', 29, [Reg8, Reg8, Reg8], globals())

LShift = Instruction('LShift', 30, [Reg8, Reg8, Reg8], globals())

RShift = Instruction('RShift', 31, [Reg8, Reg8, Reg8], globals())

URshift = Instruction('URshift', 32, [Reg8, Reg8, Reg8], globals())

BitAnd = Instruction('BitAnd', 33, [Reg8, Reg8, Reg8], globals())

BitXor = Instruction('BitXor', 34, [Reg8, Reg8, Reg8], globals())

BitOr = Instruction('BitOr', 35, [Reg8, Reg8, Reg8], globals())

InstanceOf = Instruction('InstanceOf', 36, [Reg8, Reg8, Reg8], globals())

IsIn = Instruction('IsIn', 37, [Reg8, Reg8, Reg8], globals())

GetEnvironment = Instruction('GetEnvironment', 38, [Reg8, UInt8], globals())

StoreToEnvironment = Instruction('StoreToEnvironment', 39, [Reg8, UInt8, Reg8], globals())

StoreToEnvironmentL = Instruction('StoreToEnvironmentL', 40, [Reg8, UInt16, Reg8], globals())

StoreNPToEnvironment = Instruction('StoreNPToEnvironment', 41, [Reg8, UInt8, Reg8], globals())

StoreNPToEnvironmentL = Instruction('StoreNPToEnvironmentL', 42, [Reg8, UInt16, Reg8], globals())

LoadFromEnvironment = Instruction('LoadFromEnvironment', 43, [Reg8, Reg8, UInt8], globals())

LoadFromEnvironmentL = Instruction('LoadFromEnvironmentL', 44, [Reg8, Reg8, UInt16], globals())

GetGlobalObject = Instruction('GetGlobalObject', 45, [Reg8], globals())

GetNewTarget = Instruction('GetNewTarget', 46, [Reg8], globals())

CreateEnvironment = Instruction('CreateEnvironment', 47, [Reg8], globals())

DeclareGlobalVar = Instruction('DeclareGlobalVar', 48, [UInt32], globals())

DeclareGlobalVar.operands[0].operand_meaning = OperandMeaning.string_id

GetByIdShort = Instruction('GetByIdShort', 49, [Reg8, Reg8, UInt8, UInt8], globals())

GetById = Instruction('GetById', 50, [Reg8, Reg8, UInt8, UInt16], globals())

GetByIdLong = Instruction('GetByIdLong', 51, [Reg8, Reg8, UInt8, UInt32], globals())

GetByIdShort.operands[3].operand_meaning = OperandMeaning.string_id

GetById.operands[3].operand_meaning = OperandMeaning.string_id

GetByIdLong.operands[3].operand_meaning = OperandMeaning.string_id

TryGetById = Instruction('TryGetById', 52, [Reg8, Reg8, UInt8, UInt16], globals())

TryGetByIdLong = Instruction('TryGetByIdLong', 53, [Reg8, Reg8, UInt8, UInt32], globals())

TryGetById.operands[3].operand_meaning = OperandMeaning.string_id

TryGetByIdLong.operands[3].operand_meaning = OperandMeaning.string_id

PutById = Instruction('PutById', 54, [Reg8, Reg8, UInt8, UInt16], globals())

PutByIdLong = Instruction('PutByIdLong', 55, [Reg8, Reg8, UInt8, UInt32], globals())

PutById.operands[3].operand_meaning = OperandMeaning.string_id

PutByIdLong.operands[3].operand_meaning = OperandMeaning.string_id

TryPutById = Instruction('TryPutById', 56, [Reg8, Reg8, UInt8, UInt16], globals())

TryPutByIdLong = Instruction('TryPutByIdLong', 57, [Reg8, Reg8, UInt8, UInt32], globals())

TryPutById.operands[3].operand_meaning = OperandMeaning.string_id

TryPutByIdLong.operands[3].operand_meaning = OperandMeaning.string_id

PutNewOwnByIdShort = Instruction('PutNewOwnByIdShort', 58, [Reg8, Reg8, UInt8], globals())

PutNewOwnById = Instruction('PutNewOwnById', 59, [Reg8, Reg8, UInt16], globals())

PutNewOwnByIdLong = Instruction('PutNewOwnByIdLong', 60, [Reg8, Reg8, UInt32], globals())

PutNewOwnByIdShort.operands[2].operand_meaning = OperandMeaning.string_id

PutNewOwnById.operands[2].operand_meaning = OperandMeaning.string_id

PutNewOwnByIdLong.operands[2].operand_meaning = OperandMeaning.string_id

PutNewOwnNEById = Instruction('PutNewOwnNEById', 61, [Reg8, Reg8, UInt16], globals())

PutNewOwnNEByIdLong = Instruction('PutNewOwnNEByIdLong', 62, [Reg8, Reg8, UInt32], globals())

PutNewOwnNEById.operands[2].operand_meaning = OperandMeaning.string_id

PutNewOwnNEByIdLong.operands[2].operand_meaning = OperandMeaning.string_id

PutOwnByIndex = Instruction('PutOwnByIndex', 63, [Reg8, Reg8, UInt8], globals())

PutOwnByIndexL = Instruction('PutOwnByIndexL', 64, [Reg8, Reg8, UInt32], globals())

PutOwnByVal = Instruction('PutOwnByVal', 65, [Reg8, Reg8, Reg8, UInt8], globals())

DelById = Instruction('DelById', 66, [Reg8, Reg8, UInt16], globals())

DelByIdLong = Instruction('DelByIdLong', 67, [Reg8, Reg8, UInt32], globals())

DelById.operands[2].operand_meaning = OperandMeaning.string_id

DelByIdLong.operands[2].operand_meaning = OperandMeaning.string_id

GetByVal = Instruction('GetByVal', 68, [Reg8, Reg8, Reg8], globals())

PutByVal = Instruction('PutByVal', 69, [Reg8, Reg8, Reg8], globals())

DelByVal = Instruction('DelByVal', 70, [Reg8, Reg8, Reg8], globals())

PutOwnGetterSetterByVal = Instruction('PutOwnGetterSetterByVal', 71, [Reg8, Reg8, Reg8, Reg8, UInt8], globals())

GetPNameList = Instruction('GetPNameList', 72, [Reg8, Reg8, Reg8, Reg8], globals())

GetNextPName = Instruction('GetNextPName', 73, [Reg8, Reg8, Reg8, Reg8, Reg8], globals())

Call = Instruction('Call', 74, [Reg8, Reg8, UInt8], globals())
Call.has_ret_target = True

Construct = Instruction('Construct', 75, [Reg8, Reg8, UInt8], globals())
Construct.has_ret_target = True

Call1 = Instruction('Call1', 76, [Reg8, Reg8, Reg8], globals())
Call1.has_ret_target = True

CallDirect = Instruction('CallDirect', 77, [Reg8, UInt8, UInt16], globals())
CallDirect.has_ret_target = True

Call2 = Instruction('Call2', 78, [Reg8, Reg8, Reg8, Reg8], globals())
Call2.has_ret_target = True

Call3 = Instruction('Call3', 79, [Reg8, Reg8, Reg8, Reg8, Reg8], globals())
Call3.has_ret_target = True

Call4 = Instruction('Call4', 80, [Reg8, Reg8, Reg8, Reg8, Reg8, Reg8], globals())
Call4.has_ret_target = True

CallLong = Instruction('CallLong', 81, [Reg8, Reg8, UInt32], globals())
CallLong.has_ret_target = True

ConstructLong = Instruction('ConstructLong', 82, [Reg8, Reg8, UInt32], globals())
ConstructLong.has_ret_target = True

CallDirectLongIndex = Instruction('CallDirectLongIndex', 83, [Reg8, UInt8, UInt32], globals())
CallDirectLongIndex.has_ret_target = True

CallBuiltin = Instruction('CallBuiltin', 84, [Reg8, UInt8, UInt8], globals())

Ret = Instruction('Ret', 85, [Reg8], globals())

Catch = Instruction('Catch', 86, [Reg8], globals())

DirectEval = Instruction('DirectEval', 87, [Reg8, Reg8], globals())

Throw = Instruction('Throw', 88, [Reg8], globals())

ThrowIfUndefinedInst = Instruction('ThrowIfUndefinedInst', 89, [Reg8], globals())

Debugger = Instruction('Debugger', 90, [], globals())

AsyncBreakCheck = Instruction('AsyncBreakCheck', 91, [], globals())

ProfilePoint = Instruction('ProfilePoint', 92, [UInt16], globals())

Unreachable = Instruction('Unreachable', 93, [], globals())

CreateClosure = Instruction('CreateClosure', 94, [Reg8, Reg8, UInt16], globals())

CreateClosureLongIndex = Instruction('CreateClosureLongIndex', 95, [Reg8, Reg8, UInt32], globals())

CreateGeneratorClosure = Instruction('CreateGeneratorClosure', 96, [Reg8, Reg8, UInt16], globals())

CreateGeneratorClosureLongIndex = Instruction('CreateGeneratorClosureLongIndex', 97, [Reg8, Reg8, UInt32], globals())

CreateThis = Instruction('CreateThis', 98, [Reg8, Reg8, Reg8], globals())

SelectObject = Instruction('SelectObject', 99, [Reg8, Reg8, Reg8], globals())

LoadParam = Instruction('LoadParam', 100, [Reg8, UInt8], globals())

LoadParamLong = Instruction('LoadParamLong', 101, [Reg8, UInt32], globals())

LoadConstUInt8 = Instruction('LoadConstUInt8', 102, [Reg8, UInt8], globals())

LoadConstInt = Instruction('LoadConstInt', 103, [Reg8, Imm32], globals())

LoadConstDouble = Instruction('LoadConstDouble', 104, [Reg8, Double], globals())

LoadConstString = Instruction('LoadConstString', 105, [Reg8, UInt16], globals())

LoadConstStringLongIndex = Instruction('LoadConstStringLongIndex', 106, [Reg8, UInt32], globals())

LoadConstString.operands[1].operand_meaning = OperandMeaning.string_id

LoadConstStringLongIndex.operands[1].operand_meaning = OperandMeaning.string_id

LoadConstUndefined = Instruction('LoadConstUndefined', 107, [Reg8], globals())

LoadConstNull = Instruction('LoadConstNull', 108, [Reg8], globals())

LoadConstTrue = Instruction('LoadConstTrue', 109, [Reg8], globals())

LoadConstFalse = Instruction('LoadConstFalse', 110, [Reg8], globals())

LoadConstZero = Instruction('LoadConstZero', 111, [Reg8], globals())

CoerceThisNS = Instruction('CoerceThisNS', 112, [Reg8, Reg8], globals())

LoadThisNS = Instruction('LoadThisNS', 113, [Reg8], globals())

ToNumber = Instruction('ToNumber', 114, [Reg8, Reg8], globals())

ToInt32 = Instruction('ToInt32', 115, [Reg8, Reg8], globals())

AddEmptyString = Instruction('AddEmptyString', 116, [Reg8, Reg8], globals())

GetArgumentsPropByVal = Instruction('GetArgumentsPropByVal', 117, [Reg8, Reg8, Reg8], globals())

GetArgumentsLength = Instruction('GetArgumentsLength', 118, [Reg8, Reg8], globals())

ReifyArguments = Instruction('ReifyArguments', 119, [Reg8], globals())

CreateRegExp = Instruction('CreateRegExp', 120, [Reg8, UInt32, UInt32, UInt32], globals())

CreateRegExp.operands[1].operand_meaning = OperandMeaning.string_id

CreateRegExp.operands[2].operand_meaning = OperandMeaning.string_id

SwitchImm = Instruction('SwitchImm', 121, [Reg8, UInt32, Addr32, UInt32, UInt32], globals())

StartGenerator = Instruction('StartGenerator', 122, [], globals())

ResumeGenerator = Instruction('ResumeGenerator', 123, [Reg8, Reg8], globals())

CompleteGenerator = Instruction('CompleteGenerator', 124, [], globals())

CreateGenerator = Instruction('CreateGenerator', 125, [Reg8, Reg8, UInt16], globals())

CreateGeneratorLongIndex = Instruction('CreateGeneratorLongIndex', 126, [Reg8, Reg8, UInt32], globals())

Jmp = Instruction('Jmp', 127, [Addr8], globals())
JmpLong = Instruction('JmpLong', 128, [Addr32], globals())

JmpTrue = Instruction('JmpTrue', 129, [Addr8, Reg8], globals())
JmpTrueLong = Instruction('JmpTrueLong', 130, [Addr32, Reg8], globals())

JmpFalse = Instruction('JmpFalse', 131, [Addr8, Reg8], globals())
JmpFalseLong = Instruction('JmpFalseLong', 132, [Addr32, Reg8], globals())

JmpUndefined = Instruction('JmpUndefined', 133, [Addr8, Reg8], globals())
JmpUndefinedLong = Instruction('JmpUndefinedLong', 134, [Addr32, Reg8], globals())

SaveGenerator = Instruction('SaveGenerator', 135, [Addr8], globals())
SaveGeneratorLong = Instruction('SaveGeneratorLong', 136, [Addr32], globals())

JLess = Instruction('JLess', 137, [Addr8, Reg8, Reg8], globals())
JLessLong = Instruction('JLessLong', 138, [Addr32, Reg8, Reg8], globals())

JNotLess = Instruction('JNotLess', 139, [Addr8, Reg8, Reg8], globals())
JNotLessLong = Instruction('JNotLessLong', 140, [Addr32, Reg8, Reg8], globals())

JLessN = Instruction('JLessN', 141, [Addr8, Reg8, Reg8], globals())
JLessNLong = Instruction('JLessNLong', 142, [Addr32, Reg8, Reg8], globals())

JNotLessN = Instruction('JNotLessN', 143, [Addr8, Reg8, Reg8], globals())
JNotLessNLong = Instruction('JNotLessNLong', 144, [Addr32, Reg8, Reg8], globals())

JLessEqual = Instruction('JLessEqual', 145, [Addr8, Reg8, Reg8], globals())
JLessEqualLong = Instruction('JLessEqualLong', 146, [Addr32, Reg8, Reg8], globals())

JNotLessEqual = Instruction('JNotLessEqual', 147, [Addr8, Reg8, Reg8], globals())
JNotLessEqualLong = Instruction('JNotLessEqualLong', 148, [Addr32, Reg8, Reg8], globals())

JLessEqualN = Instruction('JLessEqualN', 149, [Addr8, Reg8, Reg8], globals())
JLessEqualNLong = Instruction('JLessEqualNLong', 150, [Addr32, Reg8, Reg8], globals())

JNotLessEqualN = Instruction('JNotLessEqualN', 151, [Addr8, Reg8, Reg8], globals())
JNotLessEqualNLong = Instruction('JNotLessEqualNLong', 152, [Addr32, Reg8, Reg8], globals())

JGreater = Instruction('JGreater', 153, [Addr8, Reg8, Reg8], globals())
JGreaterLong = Instruction('JGreaterLong', 154, [Addr32, Reg8, Reg8], globals())

JNotGreater = Instruction('JNotGreater', 155, [Addr8, Reg8, Reg8], globals())
JNotGreaterLong = Instruction('JNotGreaterLong', 156, [Addr32, Reg8, Reg8], globals())

JGreaterN = Instruction('JGreaterN', 157, [Addr8, Reg8, Reg8], globals())
JGreaterNLong = Instruction('JGreaterNLong', 158, [Addr32, Reg8, Reg8], globals())

JNotGreaterN = Instruction('JNotGreaterN', 159, [Addr8, Reg8, Reg8], globals())
JNotGreaterNLong = Instruction('JNotGreaterNLong', 160, [Addr32, Reg8, Reg8], globals())

JGreaterEqual = Instruction('JGreaterEqual', 161, [Addr8, Reg8, Reg8], globals())
JGreaterEqualLong = Instruction('JGreaterEqualLong', 162, [Addr32, Reg8, Reg8], globals())

JNotGreaterEqual = Instruction('JNotGreaterEqual', 163, [Addr8, Reg8, Reg8], globals())
JNotGreaterEqualLong = Instruction('JNotGreaterEqualLong', 164, [Addr32, Reg8, Reg8], globals())

JGreaterEqualN = Instruction('JGreaterEqualN', 165, [Addr8, Reg8, Reg8], globals())
JGreaterEqualNLong = Instruction('JGreaterEqualNLong', 166, [Addr32, Reg8, Reg8], globals())

JNotGreaterEqualN = Instruction('JNotGreaterEqualN', 167, [Addr8, Reg8, Reg8], globals())
JNotGreaterEqualNLong = Instruction('JNotGreaterEqualNLong', 168, [Addr32, Reg8, Reg8], globals())

JEqual = Instruction('JEqual', 169, [Addr8, Reg8, Reg8], globals())
JEqualLong = Instruction('JEqualLong', 170, [Addr32, Reg8, Reg8], globals())

JNotEqual = Instruction('JNotEqual', 171, [Addr8, Reg8, Reg8], globals())
JNotEqualLong = Instruction('JNotEqualLong', 172, [Addr32, Reg8, Reg8], globals())

JStrictEqual = Instruction('JStrictEqual', 173, [Addr8, Reg8, Reg8], globals())
JStrictEqualLong = Instruction('JStrictEqualLong', 174, [Addr32, Reg8, Reg8], globals())

JStrictNotEqual = Instruction('JStrictNotEqual', 175, [Addr8, Reg8, Reg8], globals())
JStrictNotEqualLong = Instruction('JStrictNotEqualLong', 176, [Addr32, Reg8, Reg8], globals())

CallDirect.operands[2].operand_meaning = OperandMeaning.function_id

CreateClosure.operands[2].operand_meaning = OperandMeaning.function_id

CreateClosureLongIndex.operands[2].operand_meaning = OperandMeaning.function_id

CreateGeneratorClosure.operands[2].operand_meaning = OperandMeaning.function_id

CreateGeneratorClosureLongIndex.operands[2].operand_meaning = OperandMeaning.function_id

CreateGenerator.operands[2].operand_meaning = OperandMeaning.function_id

CreateGeneratorLongIndex.operands[2].operand_meaning = OperandMeaning.function_id

_opcode_to_instruction : Dict[int, Instruction] = {v.opcode: v for v in _instructions}
_name_to_instruction : Dict[str, Instruction] = {v.name: v for v in _instructions}

_builtin_function_names : List[str] = [
    'Array.isArray',
    'ArrayBuffer.isView',
    'Date.UTC',
    'Date.now',
    'Date.parse',
    'HermesInternal.getEpilogues',
    'HermesInternal.silentSetPrototypeOf',
    'HermesInternal.requireFast',
    'HermesInternal.getTemplateObject',
    'HermesInternal.ensureObject',
    'HermesInternal.throwTypeError',
    'HermesInternal.generatorSetDelegated',
    'HermesInternal.copyDataProperties',
    'HermesInternal.copyRestArgs',
    'HermesInternal.arraySpread',
    'HermesInternal.exportAll',
    'HermesInternal.exponentiationOperator',
    'JSON.parse',
    'JSON.stringify',
    'Math.abs',
    'Math.acos',
    'Math.asin',
    'Math.atan',
    'Math.atan2',
    'Math.ceil',
    'Math.cos',
    'Math.exp',
    'Math.floor',
    'Math.hypot',
    'Math.imul',
    'Math.log',
    'Math.max',
    'Math.min',
    'Math.pow',
    'Math.random',
    'Math.round',
    'Math.sin',
    'Math.sqrt',
    'Math.tan',
    'Math.trunc',
    'Object.create',
    'Object.defineProperties',
    'Object.defineProperty',
    'Object.freeze',
    'Object.getOwnPropertyDescriptor',
    'Object.getOwnPropertyNames',
    'Object.getPrototypeOf',
    'Object.isExtensible',
    'Object.isFrozen',
    'Object.keys',
    'Object.seal',
    'String.fromCharCode'
]

