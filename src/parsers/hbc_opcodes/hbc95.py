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

Unreachable = Instruction('Unreachable', 0, [], globals())

NewObjectWithBuffer = Instruction('NewObjectWithBuffer', 1, [Reg8, UInt16, UInt16, UInt16, UInt16], globals())

NewObjectWithBufferLong = Instruction('NewObjectWithBufferLong', 2, [Reg8, UInt16, UInt16, UInt32, UInt32], globals())

NewObject = Instruction('NewObject', 3, [Reg8], globals())

NewObjectWithParent = Instruction('NewObjectWithParent', 4, [Reg8, Reg8], globals())

NewArrayWithBuffer = Instruction('NewArrayWithBuffer', 5, [Reg8, UInt16, UInt16, UInt16], globals())

NewArrayWithBufferLong = Instruction('NewArrayWithBufferLong', 6, [Reg8, UInt16, UInt16, UInt32], globals())

NewArray = Instruction('NewArray', 7, [Reg8, UInt16], globals())

Mov = Instruction('Mov', 8, [Reg8, Reg8], globals())

MovLong = Instruction('MovLong', 9, [Reg32, Reg32], globals())

Negate = Instruction('Negate', 10, [Reg8, Reg8], globals())

Not = Instruction('Not', 11, [Reg8, Reg8], globals())

BitNot = Instruction('BitNot', 12, [Reg8, Reg8], globals())

TypeOf = Instruction('TypeOf', 13, [Reg8, Reg8], globals())

Eq = Instruction('Eq', 14, [Reg8, Reg8, Reg8], globals())

StrictEq = Instruction('StrictEq', 15, [Reg8, Reg8, Reg8], globals())

Neq = Instruction('Neq', 16, [Reg8, Reg8, Reg8], globals())

StrictNeq = Instruction('StrictNeq', 17, [Reg8, Reg8, Reg8], globals())

Less = Instruction('Less', 18, [Reg8, Reg8, Reg8], globals())

LessEq = Instruction('LessEq', 19, [Reg8, Reg8, Reg8], globals())

Greater = Instruction('Greater', 20, [Reg8, Reg8, Reg8], globals())

GreaterEq = Instruction('GreaterEq', 21, [Reg8, Reg8, Reg8], globals())

Add = Instruction('Add', 22, [Reg8, Reg8, Reg8], globals())

AddN = Instruction('AddN', 23, [Reg8, Reg8, Reg8], globals())

Mul = Instruction('Mul', 24, [Reg8, Reg8, Reg8], globals())

MulN = Instruction('MulN', 25, [Reg8, Reg8, Reg8], globals())

Div = Instruction('Div', 26, [Reg8, Reg8, Reg8], globals())

DivN = Instruction('DivN', 27, [Reg8, Reg8, Reg8], globals())

Mod = Instruction('Mod', 28, [Reg8, Reg8, Reg8], globals())

Sub = Instruction('Sub', 29, [Reg8, Reg8, Reg8], globals())

SubN = Instruction('SubN', 30, [Reg8, Reg8, Reg8], globals())

LShift = Instruction('LShift', 31, [Reg8, Reg8, Reg8], globals())

RShift = Instruction('RShift', 32, [Reg8, Reg8, Reg8], globals())

URshift = Instruction('URshift', 33, [Reg8, Reg8, Reg8], globals())

BitAnd = Instruction('BitAnd', 34, [Reg8, Reg8, Reg8], globals())

BitXor = Instruction('BitXor', 35, [Reg8, Reg8, Reg8], globals())

BitOr = Instruction('BitOr', 36, [Reg8, Reg8, Reg8], globals())

Inc = Instruction('Inc', 37, [Reg8, Reg8], globals())

Dec = Instruction('Dec', 38, [Reg8, Reg8], globals())

InstanceOf = Instruction('InstanceOf', 39, [Reg8, Reg8, Reg8], globals())

IsIn = Instruction('IsIn', 40, [Reg8, Reg8, Reg8], globals())

GetEnvironment = Instruction('GetEnvironment', 41, [Reg8, UInt8], globals())

StoreToEnvironment = Instruction('StoreToEnvironment', 42, [Reg8, UInt8, Reg8], globals())

StoreToEnvironmentL = Instruction('StoreToEnvironmentL', 43, [Reg8, UInt16, Reg8], globals())

StoreNPToEnvironment = Instruction('StoreNPToEnvironment', 44, [Reg8, UInt8, Reg8], globals())

StoreNPToEnvironmentL = Instruction('StoreNPToEnvironmentL', 45, [Reg8, UInt16, Reg8], globals())

LoadFromEnvironment = Instruction('LoadFromEnvironment', 46, [Reg8, Reg8, UInt8], globals())

LoadFromEnvironmentL = Instruction('LoadFromEnvironmentL', 47, [Reg8, Reg8, UInt16], globals())

GetGlobalObject = Instruction('GetGlobalObject', 48, [Reg8], globals())

GetNewTarget = Instruction('GetNewTarget', 49, [Reg8], globals())

CreateEnvironment = Instruction('CreateEnvironment', 50, [Reg8], globals())

CreateInnerEnvironment = Instruction('CreateInnerEnvironment', 51, [Reg8, Reg8, UInt32], globals())

DeclareGlobalVar = Instruction('DeclareGlobalVar', 52, [UInt32], globals())

DeclareGlobalVar.operands[0].operand_meaning = OperandMeaning.string_id

ThrowIfHasRestrictedGlobalProperty = Instruction('ThrowIfHasRestrictedGlobalProperty', 53, [UInt32], globals())

ThrowIfHasRestrictedGlobalProperty.operands[0].operand_meaning = OperandMeaning.string_id

GetByIdShort = Instruction('GetByIdShort', 54, [Reg8, Reg8, UInt8, UInt8], globals())

GetById = Instruction('GetById', 55, [Reg8, Reg8, UInt8, UInt16], globals())

GetByIdLong = Instruction('GetByIdLong', 56, [Reg8, Reg8, UInt8, UInt32], globals())

GetByIdShort.operands[3].operand_meaning = OperandMeaning.string_id

GetById.operands[3].operand_meaning = OperandMeaning.string_id

GetByIdLong.operands[3].operand_meaning = OperandMeaning.string_id

TryGetById = Instruction('TryGetById', 57, [Reg8, Reg8, UInt8, UInt16], globals())

TryGetByIdLong = Instruction('TryGetByIdLong', 58, [Reg8, Reg8, UInt8, UInt32], globals())

TryGetById.operands[3].operand_meaning = OperandMeaning.string_id

TryGetByIdLong.operands[3].operand_meaning = OperandMeaning.string_id

PutById = Instruction('PutById', 59, [Reg8, Reg8, UInt8, UInt16], globals())

PutByIdLong = Instruction('PutByIdLong', 60, [Reg8, Reg8, UInt8, UInt32], globals())

PutById.operands[3].operand_meaning = OperandMeaning.string_id

PutByIdLong.operands[3].operand_meaning = OperandMeaning.string_id

TryPutById = Instruction('TryPutById', 61, [Reg8, Reg8, UInt8, UInt16], globals())

TryPutByIdLong = Instruction('TryPutByIdLong', 62, [Reg8, Reg8, UInt8, UInt32], globals())

TryPutById.operands[3].operand_meaning = OperandMeaning.string_id

TryPutByIdLong.operands[3].operand_meaning = OperandMeaning.string_id

PutNewOwnByIdShort = Instruction('PutNewOwnByIdShort', 63, [Reg8, Reg8, UInt8], globals())

PutNewOwnById = Instruction('PutNewOwnById', 64, [Reg8, Reg8, UInt16], globals())

PutNewOwnByIdLong = Instruction('PutNewOwnByIdLong', 65, [Reg8, Reg8, UInt32], globals())

PutNewOwnByIdShort.operands[2].operand_meaning = OperandMeaning.string_id

PutNewOwnById.operands[2].operand_meaning = OperandMeaning.string_id

PutNewOwnByIdLong.operands[2].operand_meaning = OperandMeaning.string_id

PutNewOwnNEById = Instruction('PutNewOwnNEById', 66, [Reg8, Reg8, UInt16], globals())

PutNewOwnNEByIdLong = Instruction('PutNewOwnNEByIdLong', 67, [Reg8, Reg8, UInt32], globals())

PutNewOwnNEById.operands[2].operand_meaning = OperandMeaning.string_id

PutNewOwnNEByIdLong.operands[2].operand_meaning = OperandMeaning.string_id

PutOwnByIndex = Instruction('PutOwnByIndex', 68, [Reg8, Reg8, UInt8], globals())

PutOwnByIndexL = Instruction('PutOwnByIndexL', 69, [Reg8, Reg8, UInt32], globals())

PutOwnByVal = Instruction('PutOwnByVal', 70, [Reg8, Reg8, Reg8, UInt8], globals())

DelById = Instruction('DelById', 71, [Reg8, Reg8, UInt16], globals())

DelByIdLong = Instruction('DelByIdLong', 72, [Reg8, Reg8, UInt32], globals())

DelById.operands[2].operand_meaning = OperandMeaning.string_id

DelByIdLong.operands[2].operand_meaning = OperandMeaning.string_id

GetByVal = Instruction('GetByVal', 73, [Reg8, Reg8, Reg8], globals())

PutByVal = Instruction('PutByVal', 74, [Reg8, Reg8, Reg8], globals())

DelByVal = Instruction('DelByVal', 75, [Reg8, Reg8, Reg8], globals())

PutOwnGetterSetterByVal = Instruction('PutOwnGetterSetterByVal', 76, [Reg8, Reg8, Reg8, Reg8, UInt8], globals())

GetPNameList = Instruction('GetPNameList', 77, [Reg8, Reg8, Reg8, Reg8], globals())

GetNextPName = Instruction('GetNextPName', 78, [Reg8, Reg8, Reg8, Reg8, Reg8], globals())

Call = Instruction('Call', 79, [Reg8, Reg8, UInt8], globals())
Call.has_ret_target = True

Construct = Instruction('Construct', 80, [Reg8, Reg8, UInt8], globals())
Construct.has_ret_target = True

Call1 = Instruction('Call1', 81, [Reg8, Reg8, Reg8], globals())
Call1.has_ret_target = True

CallDirect = Instruction('CallDirect', 82, [Reg8, UInt8, UInt16], globals())

CallDirect.operands[2].operand_meaning = OperandMeaning.function_id
CallDirect.has_ret_target = True

Call2 = Instruction('Call2', 83, [Reg8, Reg8, Reg8, Reg8], globals())
Call2.has_ret_target = True

Call3 = Instruction('Call3', 84, [Reg8, Reg8, Reg8, Reg8, Reg8], globals())
Call3.has_ret_target = True

Call4 = Instruction('Call4', 85, [Reg8, Reg8, Reg8, Reg8, Reg8, Reg8], globals())
Call4.has_ret_target = True

CallLong = Instruction('CallLong', 86, [Reg8, Reg8, UInt32], globals())
CallLong.has_ret_target = True

ConstructLong = Instruction('ConstructLong', 87, [Reg8, Reg8, UInt32], globals())
ConstructLong.has_ret_target = True

CallDirectLongIndex = Instruction('CallDirectLongIndex', 88, [Reg8, UInt8, UInt32], globals())
CallDirectLongIndex.has_ret_target = True

CallBuiltin = Instruction('CallBuiltin', 89, [Reg8, UInt8, UInt8], globals())

CallBuiltinLong = Instruction('CallBuiltinLong', 90, [Reg8, UInt8, UInt32], globals())

GetBuiltinClosure = Instruction('GetBuiltinClosure', 91, [Reg8, UInt8], globals())

Ret = Instruction('Ret', 92, [Reg8], globals())

Catch = Instruction('Catch', 93, [Reg8], globals())

DirectEval = Instruction('DirectEval', 94, [Reg8, Reg8, UInt8], globals())

Throw = Instruction('Throw', 95, [Reg8], globals())

ThrowIfEmpty = Instruction('ThrowIfEmpty', 96, [Reg8, Reg8], globals())

Debugger = Instruction('Debugger', 97, [], globals())

AsyncBreakCheck = Instruction('AsyncBreakCheck', 98, [], globals())

ProfilePoint = Instruction('ProfilePoint', 99, [UInt16], globals())

CreateClosure = Instruction('CreateClosure', 100, [Reg8, Reg8, UInt16], globals())

CreateClosureLongIndex = Instruction('CreateClosureLongIndex', 101, [Reg8, Reg8, UInt32], globals())

CreateClosure.operands[2].operand_meaning = OperandMeaning.function_id

CreateClosureLongIndex.operands[2].operand_meaning = OperandMeaning.function_id

CreateGeneratorClosure = Instruction('CreateGeneratorClosure', 102, [Reg8, Reg8, UInt16], globals())

CreateGeneratorClosureLongIndex = Instruction('CreateGeneratorClosureLongIndex', 103, [Reg8, Reg8, UInt32], globals())

CreateGeneratorClosure.operands[2].operand_meaning = OperandMeaning.function_id

CreateGeneratorClosureLongIndex.operands[2].operand_meaning = OperandMeaning.function_id

CreateAsyncClosure = Instruction('CreateAsyncClosure', 104, [Reg8, Reg8, UInt16], globals())

CreateAsyncClosureLongIndex = Instruction('CreateAsyncClosureLongIndex', 105, [Reg8, Reg8, UInt32], globals())

CreateAsyncClosure.operands[2].operand_meaning = OperandMeaning.function_id

CreateAsyncClosureLongIndex.operands[2].operand_meaning = OperandMeaning.function_id

CreateThis = Instruction('CreateThis', 106, [Reg8, Reg8, Reg8], globals())

SelectObject = Instruction('SelectObject', 107, [Reg8, Reg8, Reg8], globals())

LoadParam = Instruction('LoadParam', 108, [Reg8, UInt8], globals())

LoadParamLong = Instruction('LoadParamLong', 109, [Reg8, UInt32], globals())

LoadConstUInt8 = Instruction('LoadConstUInt8', 110, [Reg8, UInt8], globals())

LoadConstInt = Instruction('LoadConstInt', 111, [Reg8, Imm32], globals())

LoadConstDouble = Instruction('LoadConstDouble', 112, [Reg8, Double], globals())

LoadConstBigInt = Instruction('LoadConstBigInt', 113, [Reg8, UInt16], globals())

LoadConstBigIntLongIndex = Instruction('LoadConstBigIntLongIndex', 114, [Reg8, UInt32], globals())

LoadConstBigInt.operands[1].operand_meaning = OperandMeaning.bigint_id

LoadConstBigIntLongIndex.operands[1].operand_meaning = OperandMeaning.bigint_id

LoadConstString = Instruction('LoadConstString', 115, [Reg8, UInt16], globals())

LoadConstStringLongIndex = Instruction('LoadConstStringLongIndex', 116, [Reg8, UInt32], globals())

LoadConstString.operands[1].operand_meaning = OperandMeaning.string_id

LoadConstStringLongIndex.operands[1].operand_meaning = OperandMeaning.string_id

LoadConstEmpty = Instruction('LoadConstEmpty', 117, [Reg8], globals())

LoadConstUndefined = Instruction('LoadConstUndefined', 118, [Reg8], globals())

LoadConstNull = Instruction('LoadConstNull', 119, [Reg8], globals())

LoadConstTrue = Instruction('LoadConstTrue', 120, [Reg8], globals())

LoadConstFalse = Instruction('LoadConstFalse', 121, [Reg8], globals())

LoadConstZero = Instruction('LoadConstZero', 122, [Reg8], globals())

CoerceThisNS = Instruction('CoerceThisNS', 123, [Reg8, Reg8], globals())

LoadThisNS = Instruction('LoadThisNS', 124, [Reg8], globals())

ToNumber = Instruction('ToNumber', 125, [Reg8, Reg8], globals())

ToNumeric = Instruction('ToNumeric', 126, [Reg8, Reg8], globals())

ToInt32 = Instruction('ToInt32', 127, [Reg8, Reg8], globals())

AddEmptyString = Instruction('AddEmptyString', 128, [Reg8, Reg8], globals())

GetArgumentsPropByVal = Instruction('GetArgumentsPropByVal', 129, [Reg8, Reg8, Reg8], globals())

GetArgumentsLength = Instruction('GetArgumentsLength', 130, [Reg8, Reg8], globals())

ReifyArguments = Instruction('ReifyArguments', 131, [Reg8], globals())

CreateRegExp = Instruction('CreateRegExp', 132, [Reg8, UInt32, UInt32, UInt32], globals())

CreateRegExp.operands[1].operand_meaning = OperandMeaning.string_id

CreateRegExp.operands[2].operand_meaning = OperandMeaning.string_id

SwitchImm = Instruction('SwitchImm', 133, [Reg8, UInt32, Addr32, UInt32, UInt32], globals())

StartGenerator = Instruction('StartGenerator', 134, [], globals())

ResumeGenerator = Instruction('ResumeGenerator', 135, [Reg8, Reg8], globals())

CompleteGenerator = Instruction('CompleteGenerator', 136, [], globals())

CreateGenerator = Instruction('CreateGenerator', 137, [Reg8, Reg8, UInt16], globals())

CreateGeneratorLongIndex = Instruction('CreateGeneratorLongIndex', 138, [Reg8, Reg8, UInt32], globals())

CreateGenerator.operands[2].operand_meaning = OperandMeaning.function_id

CreateGeneratorLongIndex.operands[2].operand_meaning = OperandMeaning.function_id

IteratorBegin = Instruction('IteratorBegin', 139, [Reg8, Reg8], globals())

IteratorNext = Instruction('IteratorNext', 140, [Reg8, Reg8, Reg8], globals())

IteratorClose = Instruction('IteratorClose', 141, [Reg8, UInt8], globals())

Jmp = Instruction('Jmp', 142, [Addr8], globals())
JmpLong = Instruction('JmpLong', 143, [Addr32], globals())

JmpTrue = Instruction('JmpTrue', 144, [Addr8, Reg8], globals())
JmpTrueLong = Instruction('JmpTrueLong', 145, [Addr32, Reg8], globals())

JmpFalse = Instruction('JmpFalse', 146, [Addr8, Reg8], globals())
JmpFalseLong = Instruction('JmpFalseLong', 147, [Addr32, Reg8], globals())

JmpUndefined = Instruction('JmpUndefined', 148, [Addr8, Reg8], globals())
JmpUndefinedLong = Instruction('JmpUndefinedLong', 149, [Addr32, Reg8], globals())

SaveGenerator = Instruction('SaveGenerator', 150, [Addr8], globals())
SaveGeneratorLong = Instruction('SaveGeneratorLong', 151, [Addr32], globals())

JLess = Instruction('JLess', 152, [Addr8, Reg8, Reg8], globals())
JLessLong = Instruction('JLessLong', 153, [Addr32, Reg8, Reg8], globals())

JNotLess = Instruction('JNotLess', 154, [Addr8, Reg8, Reg8], globals())
JNotLessLong = Instruction('JNotLessLong', 155, [Addr32, Reg8, Reg8], globals())

JLessN = Instruction('JLessN', 156, [Addr8, Reg8, Reg8], globals())
JLessNLong = Instruction('JLessNLong', 157, [Addr32, Reg8, Reg8], globals())

JNotLessN = Instruction('JNotLessN', 158, [Addr8, Reg8, Reg8], globals())
JNotLessNLong = Instruction('JNotLessNLong', 159, [Addr32, Reg8, Reg8], globals())

JLessEqual = Instruction('JLessEqual', 160, [Addr8, Reg8, Reg8], globals())
JLessEqualLong = Instruction('JLessEqualLong', 161, [Addr32, Reg8, Reg8], globals())

JNotLessEqual = Instruction('JNotLessEqual', 162, [Addr8, Reg8, Reg8], globals())
JNotLessEqualLong = Instruction('JNotLessEqualLong', 163, [Addr32, Reg8, Reg8], globals())

JLessEqualN = Instruction('JLessEqualN', 164, [Addr8, Reg8, Reg8], globals())
JLessEqualNLong = Instruction('JLessEqualNLong', 165, [Addr32, Reg8, Reg8], globals())

JNotLessEqualN = Instruction('JNotLessEqualN', 166, [Addr8, Reg8, Reg8], globals())
JNotLessEqualNLong = Instruction('JNotLessEqualNLong', 167, [Addr32, Reg8, Reg8], globals())

JGreater = Instruction('JGreater', 168, [Addr8, Reg8, Reg8], globals())
JGreaterLong = Instruction('JGreaterLong', 169, [Addr32, Reg8, Reg8], globals())

JNotGreater = Instruction('JNotGreater', 170, [Addr8, Reg8, Reg8], globals())
JNotGreaterLong = Instruction('JNotGreaterLong', 171, [Addr32, Reg8, Reg8], globals())

JGreaterN = Instruction('JGreaterN', 172, [Addr8, Reg8, Reg8], globals())
JGreaterNLong = Instruction('JGreaterNLong', 173, [Addr32, Reg8, Reg8], globals())

JNotGreaterN = Instruction('JNotGreaterN', 174, [Addr8, Reg8, Reg8], globals())
JNotGreaterNLong = Instruction('JNotGreaterNLong', 175, [Addr32, Reg8, Reg8], globals())

JGreaterEqual = Instruction('JGreaterEqual', 176, [Addr8, Reg8, Reg8], globals())
JGreaterEqualLong = Instruction('JGreaterEqualLong', 177, [Addr32, Reg8, Reg8], globals())

JNotGreaterEqual = Instruction('JNotGreaterEqual', 178, [Addr8, Reg8, Reg8], globals())
JNotGreaterEqualLong = Instruction('JNotGreaterEqualLong', 179, [Addr32, Reg8, Reg8], globals())

JGreaterEqualN = Instruction('JGreaterEqualN', 180, [Addr8, Reg8, Reg8], globals())
JGreaterEqualNLong = Instruction('JGreaterEqualNLong', 181, [Addr32, Reg8, Reg8], globals())

JNotGreaterEqualN = Instruction('JNotGreaterEqualN', 182, [Addr8, Reg8, Reg8], globals())
JNotGreaterEqualNLong = Instruction('JNotGreaterEqualNLong', 183, [Addr32, Reg8, Reg8], globals())

JEqual = Instruction('JEqual', 184, [Addr8, Reg8, Reg8], globals())
JEqualLong = Instruction('JEqualLong', 185, [Addr32, Reg8, Reg8], globals())

JNotEqual = Instruction('JNotEqual', 186, [Addr8, Reg8, Reg8], globals())
JNotEqualLong = Instruction('JNotEqualLong', 187, [Addr32, Reg8, Reg8], globals())

JStrictEqual = Instruction('JStrictEqual', 188, [Addr8, Reg8, Reg8], globals())
JStrictEqualLong = Instruction('JStrictEqualLong', 189, [Addr32, Reg8, Reg8], globals())

JStrictNotEqual = Instruction('JStrictNotEqual', 190, [Addr8, Reg8, Reg8], globals())
JStrictNotEqualLong = Instruction('JStrictNotEqualLong', 191, [Addr32, Reg8, Reg8], globals())

Add32 = Instruction('Add32', 192, [Reg8, Reg8, Reg8], globals())

Sub32 = Instruction('Sub32', 193, [Reg8, Reg8, Reg8], globals())

Mul32 = Instruction('Mul32', 194, [Reg8, Reg8, Reg8], globals())

Divi32 = Instruction('Divi32', 195, [Reg8, Reg8, Reg8], globals())

Divu32 = Instruction('Divu32', 196, [Reg8, Reg8, Reg8], globals())

Loadi8 = Instruction('Loadi8', 197, [Reg8, Reg8, Reg8], globals())

Loadu8 = Instruction('Loadu8', 198, [Reg8, Reg8, Reg8], globals())

Loadi16 = Instruction('Loadi16', 199, [Reg8, Reg8, Reg8], globals())

Loadu16 = Instruction('Loadu16', 200, [Reg8, Reg8, Reg8], globals())

Loadi32 = Instruction('Loadi32', 201, [Reg8, Reg8, Reg8], globals())

Loadu32 = Instruction('Loadu32', 202, [Reg8, Reg8, Reg8], globals())

Store8 = Instruction('Store8', 203, [Reg8, Reg8, Reg8], globals())

Store16 = Instruction('Store16', 204, [Reg8, Reg8, Reg8], globals())

Store32 = Instruction('Store32', 205, [Reg8, Reg8, Reg8], globals())

_opcode_to_instruction : Dict[int, Instruction] = {v.opcode: v for v in _instructions}
_name_to_instruction : Dict[str, Instruction] = {v.name: v for v in _instructions}

_builtin_function_names : List[str] = [
    'Array.isArray',
    'Date.UTC',
    'Date.parse',
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
    'String.fromCharCode',
    'silentSetPrototypeOf',
    'requireFast',
    'getTemplateObject',
    'ensureObject',
    'getMethod',
    'throwTypeError',
    'generatorSetDelegated',
    'copyDataProperties',
    'copyRestArgs',
    'arraySpread',
    'apply',
    'exportAll',
    'exponentiationOperator',
    'initRegexNamedGroups',
    'getOriginalNativeErrorConstructor',
    'spawnAsync'
]

