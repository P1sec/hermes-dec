#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Union, Any, Sequence, Dict, Set, Optional
from dataclasses import dataclass
from enum import IntEnum, IntFlag
from struct import unpack
from io import BytesIO

"""
    The SerializedLiteral format is used to store structured
    arrays of string references and literals within the Hermes
    array buffer, object key buffer, object value buffer
    arrays.
    
    It is parsed here:
    
        https://github.com/facebook/hermes/blob/v0.12.0/lib/BCGen/HBC/BytecodeDisassembler.cpp#L285
    
  OS << "Object Key Buffer:\n";
  while ((size_t)keyInd < objKeyBuffer.size()) {
    std::pair<int, SLG::TagType> keyTag =
        checkBufferTag(objKeyBuffer.data() + keyInd);
    keyInd += (keyTag.first > 0x0f ? 2 : 1);
    for (int i = 0; i < keyTag.first; i++) {
      OS << SLPToString(keyTag.second, objKeyBuffer.data(), &keyInd) << "\n";
    }
  }

    
    Strings are referred to as indexes of the global string,
    which are stored over either 8, 16 or 32 bits each:
    
        int ind =
            isKeyBuffer ? BMGen_.getIdentifierID(str) : BMGen_.getStringID(str);
    
    The binary form of this format is TLV-oriented, see:
    
    https://github.com/facebook/hermes/blob/v0.12.0/include/hermes/BCGen/HBC/SerializedLiteralGenerator.h
    https://github.com/facebook/hermes/blob/v0.12.0/lib/BCGen/HBC/SerializedLiteralParserBase.cpp
    https://github.com/facebook/hermes/blob/v0.12.0/lib/BCGen/HBC/SerializedLiteralGenerator.cpp
    https://github.com/facebook/hermes/blob/v0.12.0/include/hermes/BCGen/HBC/SerializedLiteralParserBase.h
    https://github.com/facebook/hermes/blob/v0.12.0/lib/VM/SerializedLiteralParser.cpp
    https://github.com/facebook/hermes/blob/v0.12.0/include/hermes/VM/SerializedLiteralParser.h
"""

class TagType(IntEnum):
    NullTag = 0
    TrueTag = 1
    FalseTag = 2
    NumberTag = 3
    LongStringTag = 4
    ShortStringTag = 5
    ByteStringTag = 6
    IntegerTag = 7
    

@dataclass
class SLPValue:
    tag_type : TagType
    
    value : object

@dataclass
class SLPArray:
    items : List[SLPValue]
    
    def to_strings(self, string_table : List[str]) -> List[str]:
        
        stringified_items : List[str] = []
        for item in self.items:
            if item.tag_type == TagType.NullTag:
                string = 'null'
            elif item.tag_type == TagType.TrueTag:
                string = 'true'
            elif item.tag_type == TagType.FalseTag:
                string = 'false'
            elif item.tag_type == TagType.NumberTag:
                string = str(item.value)
            elif item.tag_type in (TagType.LongStringTag,
                TagType.ShortStringTag, TagType.ByteStringTag):
                string = repr(string_table[item.value])
            elif item.tag_type == TagType.IntegerTag:
                string = str(item.value)
            else:
                raise ValueError
            
            stringified_items.append(string)
    
        return stringified_items
    

def unpack_slp_array(data : bytes, num_items : int) -> SLPArray:
    data = BytesIO(data)
    
    items = []
    
    while len(items) < num_items:
        values = []
        
        next_tag = data.read(1)
        if not next_tag:
            break
        tag_type = TagType((next_tag[0] >> 4) & 0b111)
        if next_tag[0] >> 7 == 1: # Extended length flag?
            length = ((next_tag[0] & 0b1111) << 8) | data.read(1)[0]
        else:
            length = next_tag[0] & 0b1111
        
        for item in range(length):
            
            if tag_type == TagType.NullTag:
                values.append(None)
            elif tag_type == TagType.TrueTag:
                values.append(True)
            elif tag_type == TagType.FalseTag:
                values.append(False)
            elif tag_type == TagType.NumberTag:
                values.append(unpack('<d', data.read(8))[0])
            elif tag_type == TagType.LongStringTag:
                values.append(int.from_bytes(data.read(4), 'little'))
            elif tag_type == TagType.ShortStringTag:
                values.append(int.from_bytes(data.read(2), 'little'))
            elif tag_type == TagType.ByteStringTag:
                values.append(int.from_bytes(data.read(1), 'little'))
            elif tag_type == TagType.IntegerTag:
                values.append(int.from_bytes(data.read(4), 'little'))
            else:
                raise ValueError
        
        items.extend(SLPValue(tag_type, value)
            for value in values)

    return SLPArray(items[:num_items])
    
