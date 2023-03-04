#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from ctypes import LittleEndianStructure, c_uint8, c_uint16, c_uint32, c_uint64, c_int8, c_int16, c_int32, c_int64
from typing import Sequence, Union, Dict, List, Set
from io import BytesIO, BufferedReader
from os.path import dirname, realpath
from argparse import ArgumentParser
from enum import IntEnum, IntFlag
from hashlib import sha1

# The following imports are made from the current directory:
from hbc_bytecode_parser import parse_hbc_bytecode, get_parser, ParsedInstruction
from regexp_bytecode_parser import decompile_regex, parse_regex
from pretty_print import pretty_print_structure
from debug_info_parser import print_debug_info

PARSERS_DIR = dirname(realpath(__file__))
ROOT_DIR = realpath(PARSERS_DIR + '/..')
TESTS_DIR = realpath(ROOT_DIR + '/tests')
ASSETS_DIR = realpath(TESTS_DIR + '/assets')

"""

    Regarding the file signature to check for, please
    refer to:
    https://github.com/file/file/blob/FILE5_43/magic/Magdir/javascript#L19

!:mime application/javascript
# Hermes by Facebook https://hermesengine.dev/
# https://github.com/facebook/hermes/blob/master/include/hermes/\
# BCGen/HBC/BytecodeFileFormat.h#L24
0	lequad		0x1F1903C103BC1FC6	Hermes JavaScript bytecode
>8	lelong		x			\b, version %d
    +
    https://github.com/facebook/hermes/blob/main/include/hermes/BCGen/HBC/BytecodeFileFormat.h#L24
    
    Especially, find the header structure for the concerned
    file format here:
        https://github.com/facebook/hermes/blob/v0.12.0/include/hermes/BCGen/HBC/BytecodeFileFormat.h#L71
        
    Parser in Python:
    
        https://github.com/bongtrop/hbctool/blob/v0.1.5/hbctool/hbc/__init__.py#L10
    
    [i] The function/method definitions in this file generally
        read from bottom to top.
"""

HEADER_MAGIC = int.from_bytes('Ἑρμῆ'.encode('utf-16be'), 'big') # 0x1f1903c103bc1fc6

LATEST_BYTECODE_VERSION = 89

SHA1_NUM_BYTES = 20

# Find the latest bytecode version up to the current day here:
# https://github.com/facebook/hermes/blob/main/include/hermes/BCGen/HBC/BytecodeVersion.h#L23

class ProhibitInvoke(IntEnum):
    
    ProhibitCall = 0
    ProhibitConstruct = 1
    ProhibitNone = 2

class StringKind(IntEnum):
    
    String = 0
    Identifier = 1
    Predefined = 2 # Unused since version 0.3.0 - merged with Identifier

class HBCReader:
    
    # The following structure will be derived from the CTypesReader
    # class which is dynamically constructured below, with fields
    # that may vary depending upon the Hermes bytecode version.
    
    header : object
    function_headers : List[object]
    function_ops : List[List[ParsedInstruction]]
    function_id_to_exc_handlers : Dict[int, List['HBCExceptionHandlerInfo']]
    function_id_to_debug_offsets : Dict[int, 'DebugOffsets']
    string_kinds : List[StringKind]
    identifier_hashes : List[int]
    
    small_string_table : List[object]
    overflow_string_table : List[object]
    string_storage : BytesIO
    strings : List[str]
    
    parser_module : 'module'
    file_buffer : BufferedReader
    
    # The following bytes can be sliced and decoded to "SLPArray"
    # objects using the "unpack_slp_array" function of
    # "serialized_literal_parser.py":
    arrays : bytes
    object_keys : bytes
    object_values : bytes
    
    bigint_values : List[int]
    
    regexp_table : List[object]
    regexp_storage : BytesIO
    
    cjs_modules : List[object]
    function_sources : List[object]
    
    debug_info_header : object
    debug_string_table : List[object]
    debug_string_storage : BytesIO
    debug_file_regions : List[object]
    sources_data_storage : BytesIO
    lexical_data_storage : BytesIO
    textified_data_storage : BytesIO
    string_table_storage : BytesIO

    def get_header_reader(self, bytecode_version : int = LATEST_BYTECODE_VERSION) -> type:
        
        class CTypesReader(LittleEndianStructure):
            _pack_ = True
        
        fields = [
            ('magic', c_uint64),
            ('version', c_uint32),
            ('sourceHash', c_uint8 * SHA1_NUM_BYTES), # This is a hash from the actual plain-text JS source.
            ('fileLength', c_uint32), # Until the end of the BytecodeFileFooter.
            ('globalCodeIndex', c_uint32),
            ('functionCount', c_uint32),
            ('stringKindCount', c_uint32), # Number of string kind entries.
            ('identifierCount', c_uint32), # Number of strings which are identifiers.
            ('stringCount', c_uint32), # Number of strings in the string table.
            ('overflowStringCount', c_uint32), # Number of strings in the overflow table.
            ('stringStorageSize', c_uint32) # Bytes in the blob of string contents.
        ]
        
        if bytecode_version >= 87:
            
            fields += [
                ('bigIntCount', c_uint32), # Added in version 0.12.0 - Bytecode version 87 # number of bigints in the bigint table.
                ('bigIntStorageSize', c_uint32) # Added in version 0.12.0 - Bytecode version 87 # Bytes in the bigint table.
            ]
        
        fields += [
            ('regExpCount', c_uint32),
            ('regExpStorageSize', c_uint32),
            ('arrayBufferSize', c_uint32),
            ('objKeyBufferSize', c_uint32),
            ('objValueBufferSize', c_uint32),
            ('cjsModuleOffset' if bytecode_version < 78 else 'segmentID', c_uint32), # Was called "cjsModuleOffset" before version 0.8.0 - Bytecode version 78 # The ID of this segment.
            ('cjsModuleCount', c_uint32) # Number of modules.
        ]
        
        if bytecode_version >= 84:
            
            fields += [
                ('functionSourceCount', c_uint32) # Added in version 0.8.1 - Bytecode version 84 # Number of function sources preserved.
            ]
        
        fields += [
            ('debugInfoOffset', c_uint32),
            
            # Options (TODO: Are we decoding it correctly, in the right order?):
            ('staticBuiltins', c_uint8, 1),
            ('cjsModulesStaticallyResolved', c_uint8, 1),
            ('hasAsync', c_uint8, 1),
        ]
        
        # After these fields, padding bytes should align
        # the file cursor over a multiple of 32 bytes.
        
        CTypesReader._fields_ = fields
        
        return CTypesReader
    
    def get_small_func_header_reader(self) -> type:
        
        # The "SmallFunctionHeader" is stored just after the
        # "BytecodeFileHeader" in the .HBC Hermes bytecode file,
        # and each entry of it contains a field which will
        # indicate whether an "extended function header" will
        # be present for the concerned function near of the
        # end of the concerned file.
        
        # It is defined here in the Hermes C++ code base:
        # a) The fields themselves, in a generic macro:
        #  https://github.com/facebook/hermes/blob/v0.12.0/include/hermes/BCGen/HBC/BytecodeFileFormat.h#L254
        # b) The structure declaration directive, instancying the aforementioned macro:
        # https://github.com/facebook/hermes/blob/v0.12.0/include/hermes/BCGen/HBC/BytecodeFileFormat.h#L313
        # c) The FunctionHeaderFlag enum:
        # https://github.com/facebook/hermes/blob/v0.12.0/include/hermes/BCGen/HBC/BytecodeFileFormat.h#L220
        
        # (the "FUNC_HEADER_FIELDS(CHECK_COPY_FIELD)" line is
        # another macro call which whether whether any of the
        # fields of the concerned structure - all the
        # corresponding fields being integers - overflow
        
        # In the hbctool project, it has been statically
        # defined here:
        # - (First) Bytecode version 59: https://github.com/bongtrop/hbctool/blob/v0.1.5/hbctool/hbc/hbc59/data/structure.json#L25
        # - (Last) Bytecode version 76: https://github.com/bongtrop/hbctool/blob/v0.1.5/hbctool/hbc/hbc76/data/structure.json#L25
        
        # - Does it has evolved through version of the .HBC format?
        # a) The field definition macro was the same within version 0.0.1 of Hermes. https://github.com/facebook/hermes/blob/v0.0.1/include/hermes/BCGen/HBC/BytecodeFileFormat.h#L225
        # b) The structure declaration directive neither: https://github.com/facebook/hermes/blob/v0.0.1/include/hermes/BCGen/HBC/BytecodeFileFormat.h#L284
        # c) The header flags bit field neither: https://github.com/facebook/hermes/blob/v0.0.1/include/hermes/BCGen/HBC/BytecodeFileFormat.h#L191
        # => We should conclude that the fields of the concerned structure should be stable across versions.
        
        class CTypesReader(LittleEndianStructure):
            _pack_ = True
            
            _fields_ = [
                # First word
                ('offset', c_uint32, 25),
                ('paramCount', c_uint32, 7),
                
                # Second word
                ('bytecodeSizeInBytes', c_uint32, 15),
                ('functionName', c_uint32, 17),
                
                # Third word
                ('infoOffset', c_uint32, 25),
                ('frameSize', c_uint32, 7),
                
                # Fourth word, with flags below
                ('environmentSize', c_uint8),
                ('highestReadCacheIndex', c_uint8),
                ('highestWriteCacheIndex', c_uint8),
                
                # Flags
                ('prohibitInvoke', c_uint8, 2), # See enum: ProhibitInvoke
                ('strictMode', c_uint8, 1),
                ('hasExceptionHandler', c_uint8, 1),
                ('hasDebugInfo', c_uint8, 1),
                ('overflowed', c_uint8, 1),
                ('unused', c_uint8, 2),
            ]
        
        return CTypesReader
    
    def get_large_func_header_reader(self):
        
        class CTypesReader(LittleEndianStructure):
            _pack_ = True # Packed?
            
            _fields_ = [
                # First word
                ('offset', c_uint32),
                ('paramCount', c_uint32),
                
                # Second word
                ('bytecodeSizeInBytes', c_uint32),
                ('functionName', c_uint32),
                
                # Third word
                ('infoOffset', c_uint32),
                ('frameSize', c_uint32),
                
                # Fourth word, with flags below
                ('environmentSize', c_uint32),
                ('highestReadCacheIndex', c_uint8),
                ('highestWriteCacheIndex', c_uint8),
                
                # Flags
                ('prohibitInvoke', c_uint8, 2), # See enum: ProhibitInvoke
                ('strictMode', c_uint8, 1),
                ('hasExceptionHandler', c_uint8, 1),
                ('hasDebugInfo', c_uint8, 1),
                ('overflowed', c_uint8, 1),
                ('unused', c_uint8, 2),
            ]
        
        return CTypesReader
        
    
    def get_string_kind_entry_reader(self) -> type:
    
        # The layout of "StringKind::Entry" was changed with
        # bytecode version 71 (the release 0.3.0 of Hermes)
        
        # Cf. https://github.com/facebook/hermes/commit/5b4a501888ee9458615457d9bf0be05a4687e027
        
        class CTypesReader(LittleEndianStructure):
            _pack_ = True
        
        if self.header.version >= 71:
            fields = [
                ('count', c_uint32, 31),
                ('kind', c_uint32, 1)
            ]
        else:
            fields = [
                ('count', c_uint32, 30),
                ('kind', c_uint32, 2)
            ]
        
        CTypesReader._fields_ = fields
        
        return CTypesReader
    
    def get_small_string_table_entry_reader(self) -> type:
        
        # "struct SmallStringTableEntry" is defined here: https://github.com/facebook/hermes/blob/v0.12.0/include/hermes/BCGen/HBC/BytecodeFileFormat.h#L169
        
        """
            Reminder of the wire level reading order of the C/C++
            bit fields:

            >>> x=X(); BytesIO(bytes([0b10111001, 0b01011010, 0b11101111, 0b10000011])).readinto(x); (x.isUTF16, x.isIdentifier, bin(x.offset), bin(x.length))
            4
            (1, 0, '0b1110111101011010101110', '0b10000011')
             A  B     CCCCCCCCDDDDDDDDEEEEEE      FFFFFFFF
            0b10111001, 0b01011010, 0b11101111, 0b10000011
              ABEEEEEE    DDDDDDDD    CCCCCCCC    FFFFFFFF
            
            This means that the "isIdentifier" field would
            occupy bit 7/23 of the "offset" field if the
            older format of this field was transposed into
            the newer corresponding format.
        """
        
        # The "isIdentifier" field was removed in version 0.0.3 -
        # bytecode version 56
        # Cf. https://github.com/facebook/hermes/commit/17816a14bad62dbccb2de75f62eb999b5973ad8b
        
        class CTypesReader(LittleEndianStructure):
            _pack_ = True
        
        if self.header.version >= 56:
            fields = [
                ('isUTF16', c_uint32, 1),
                ('offset', c_uint32, 23),
                ('length', c_uint32, 8)
            ]
        else:
            fields = [
                ('isUTF16', c_uint32, 1),
                ('isIdentifier', c_uint32, 1), # Was removed because "Only used for asserts"
                ('offset', c_uint32, 22),
                ('length', c_uint32, 8)
            ]
        
        CTypesReader._fields_ = fields
        
        return CTypesReader
    
    def get_offset_length_pair_reader(self) -> type:
        
        # BigIntTableEntry is defines here as a structure:
        # https://github.com/facebook/hermes/blob/v0.12.0/include/hermes/Support/BigIntSupport.h#L418
        
        class CTypesReader(LittleEndianStructure):
            _pack_ = True
            _fields_ = [
                ('offset', c_uint32),
                ('length', c_uint32)
            ]
        
        return CTypesReader
    
    def get_symbol_offset_pair_reader(self) -> type:
        
        class CTypesReader(LittleEndianStructure):
            _pack_ = True
            _fields_ = [
                ('symbol_id', c_uint32),
                ('offset', c_uint32)
            ]
        
        return CTypesReader
    
    def get_function_source_entry_reader(self) -> type:
        
        class CTypesReader(LittleEndianStructure):
            _pack_ = True
            _fields_ = [
                ('function_id', c_uint32),
                ('string_id', c_uint32)
            ]
        
        return CTypesReader
    
    def get_debug_info_header_reader(self) -> type:
        
        class CTypesReader(LittleEndianStructure):
            _pack_ = True
        
        if self.header.version >= 91:
            
            fields = [
                ('filename_count', c_uint32),
                ('filename_storage_size', c_uint32),
                ('file_region_count', c_uint32),
                ('lexical_data_offset', c_uint32),
                ('textified_data_offset', c_uint32),
                ('string_table_offset', c_uint32),
                ('debug_data_size', c_uint32)
            ]
        
        else:
        
            fields = [
                ('filename_count', c_uint32),
                ('filename_storage_size', c_uint32),
                ('file_region_count', c_uint32),
                ('lexical_data_offset', c_uint32),
                ('debug_data_size', c_uint32)
            ]
        
        CTypesReader._fields_ = fields
        
        return CTypesReader
    
    def get_debug_file_region_reader(self) -> type:
        
        class CTypesReader(LittleEndianStructure):
            _pack_ = True
            _fields_ = [
                ('from_address', c_uint32),
                ('filename_id', c_uint32),
                ('source_mapping_id', c_uint32)
            ]
        
        return CTypesReader
    
    def get_exception_handler_info_reader(self) -> type:
        
        class CTypesReader(LittleEndianStructure):
            _pack_ = True
            _fields_ = [
                ('start', c_uint32),
                ('end', c_uint32),
                ('target', c_uint32)
            ]
        
        return CTypesReader
    
    def get_debug_offsets_reader(self) -> type:
        
        class CTypesReader(LittleEndianStructure):
            _pack_ = True
        
        if self.header.version >= 91:
            fields = [
                ('source_locations', c_uint32),
                ('lexical_data', c_uint32),
                ('textified_callees', c_uint32)
            ]
        
        else:
            fields = [
                ('source_locations', c_uint32),
                ('lexical_data', c_uint32)
            ]
        
        CTypesReader._fields_ = fields
        
        return CTypesReader
    
    def align_over_padding(self, padding_amount = 4):
        
        # Each bytecode segment should be padded over
        # the size of an uint32_t
        
        current_pos = self.file_buffer.tell()
        
        if current_pos % padding_amount != 0:
            self.file_buffer.read(-current_pos % padding_amount)

    def read_header_from_buffer(self):
        
        # Check for a valid file header, and read the bytecode
        # format version (it will be required for properly
        # decoding the header fields)
        
        self.file_buffer.seek(0)
        magic = int.from_bytes(self.file_buffer.read(8), 'little')
        if magic != HEADER_MAGIC:
            raise ValueError('This file does not have the magic header for a Hermes bytecode file.')
        
        version = int.from_bytes(self.file_buffer.read(4), 'little')
        self.parser_module = get_parser(version)
        
        self.file_buffer.read(SHA1_NUM_BYTES) # Skip file hash
        
        file_size = int.from_bytes(self.file_buffer.read(4), 'little')
        
        # Check the SHA-1 footer located at the end of the .HBC
        # bytecode file (the single-field BytecodeFileFooter structure)
        
        if version >= 75:
            self.file_buffer.seek(0)
            file_data = self.file_buffer.read(file_size)
            assert sha1(file_data[:-SHA1_NUM_BYTES]).digest() == file_data[-SHA1_NUM_BYTES:]
        
        # Decode the BytecodeFileHeader structure and
        # return it to the caller
        
        self.file_buffer.seek(0)
        
        header_reader = self.get_header_reader(version)()
        self.file_buffer.readinto(header_reader)
        
        self.align_over_padding(32)
        
        self.header = header_reader
    
    def read_functions(self):
        
        self.function_headers = []
        self.function_ops = []
        
        self.function_id_to_exc_handlers = {}
        self.function_id_to_debug_offsets = {}
        
        self.align_over_padding()
        
        reader = self.get_small_func_header_reader()
        reader_large = self.get_large_func_header_reader()
        
        for function_count in range(self.header.functionCount):
            
            function_header = reader()
            
            self.file_buffer.readinto(function_header)
            
            before_pos = self.file_buffer.tell()
            
            # Read the overflowed header, if any:
            if function_header.overflowed:
                new_offset = (function_header.infoOffset << 16) | function_header.offset
                function_header = reader_large()
                
                self.file_buffer.seek(new_offset)
                
                self.file_buffer.readinto(function_header)
            
            else:
                self.file_buffer.seek(function_header.infoOffset)
            
            self.function_headers.append(function_header)
            
            # Read the exception handler information, if any
             
            if function_header.hasExceptionHandler:
                self.align_over_padding()
                
                exc_headers_count = int.from_bytes(self.file_buffer.read(4), 'little')
                exc_headers = (self.get_exception_handler_info_reader() * exc_headers_count)()
                self.file_buffer.readinto(exc_headers)
                
                self.function_id_to_exc_handlers[function_count] = exc_headers
                
            # Read the debug information, if any
            
            if function_header.hasDebugInfo:
                self.align_over_padding()
                
                debug_header = self.get_debug_offsets_reader()()
                self.file_buffer.readinto(debug_header)
                
                self.function_id_to_debug_offsets[function_count] = debug_header
            
            # Read and parse the actual bytecode (+ switch tables) using
            # the "hbc_bytecode_parser.py" file:
            
            self.file_buffer.seek(function_header.offset)
            
            data = self.file_buffer.read(function_header.bytecodeSizeInBytes)
            function_ops = parse_hbc_bytecode(BytesIO(data), function_header.offset, self.header.version, self)
            
            self.file_buffer.seek(before_pos)
            
            self.function_ops.append(function_ops)
    
    def read_string_kinds(self):
        
        self.string_kinds = []
        
        self.align_over_padding()
        
        reader = self.get_string_kind_entry_reader()
        
        for string_kind_count in range(self.header.stringKindCount):
            
            string_kind = reader()
            
            self.file_buffer.readinto(string_kind)
            
            # Decode the run-length encoding instead of
            # storing the raw structure:
            self.string_kinds += [StringKind(string_kind.kind)] * string_kind.count
    
    def read_identifier_hashes(self):
        
        self.align_over_padding()
        
        self.identifier_hashes = [
            int.from_bytes(self.file_buffer.read(4), 'little')
            for identifier_count in range(self.header.identifierCount)
        ]
    
    def read_small_string_table(self):
        
        self.align_over_padding()
        
        self.small_string_table = (self.get_small_string_table_entry_reader() *
            self.header.stringCount)()
        
        self.file_buffer.readinto(self.small_string_table)
    
    def read_overflow_string_table(self):
        
        self.align_over_padding()
        
        self.overflow_string_table = (self.get_offset_length_pair_reader() *
            self.header.overflowStringCount)()
        
        self.file_buffer.readinto(self.overflow_string_table)
        
    def read_string_storage(self):
        
        self.strings = []
        
        self.align_over_padding()
        
        self.string_storage = BytesIO(self.file_buffer.read(
            self.header.stringStorageSize))
        
        for string_count in range(self.header.stringCount):
            
            info = self.small_string_table[string_count]
            is_utf_16 = info.isUTF16
            if info.length == 0xff:
                info = self.overflow_string_table[info.offset]
            length = info.length
            offset = info.offset
            
            if is_utf_16:
                length *= 2
            self.string_storage.seek(offset)
            string = self.string_storage.read(length)
            assert len(string) == length
            if is_utf_16:
                string = string.decode('utf-16', errors = 'surrogatepass')
            else:
                string = ''.join(chr(char) for char in string)
            
            self.strings.append(string)
    
    def read_arrays(self):
        
        self.align_over_padding()
        self.arrays = self.file_buffer.read(self.header.arrayBufferSize)
        
        self.align_over_padding()
        self.object_keys = self.file_buffer.read(self.header.objKeyBufferSize)
        
        self.align_over_padding()
        self.object_values = self.file_buffer.read(self.header.objValueBufferSize)
    
    def read_bigints(self):
        
        self.align_over_padding()
        
        bigint_table = (self.get_offset_length_pair_reader() *
            self.header.bigIntCount)()
        
        self.file_buffer.readinto(bigint_table)
        
        self.align_over_padding()
        
        bigint_data = self.file_buffer.read(self.header.bigIntStorageSize)
        
        self.bigint_values = [int.from_bytes(bigint_data[
            entry.offset:entry.offset + entry.length], 'little')
            for entry in bigint_table]
    
    def read_regexp(self):
        
        self.align_over_padding()
        
        self.regexp_table = (self.get_offset_length_pair_reader() *
            self.header.regExpCount)()
        
        self.file_buffer.readinto(self.regexp_table)
        
        self.align_over_padding()
        
        self.regexp_storage = BytesIO(self.file_buffer.read(
            self.header.regExpStorageSize))
        
        # (We have implemented a RegExp bytecode decoder in the
        # neighboring "regexp_bytecode_parser.py" file.)
    
    def read_cjs_modules(self):
        
        self.align_over_padding()
        
        self.cjs_modules = (self.get_symbol_offset_pair_reader() *
            self.header.cjsModuleCount)()
        
        self.file_buffer.readinto(self.cjs_modules)
    
    def read_function_sources(self):
        
        self.align_over_padding()
        
        self.function_sources = (self.get_function_source_entry_reader() *
            self.header.functionSourceCount)()
        
        self.file_buffer.readinto(self.function_sources)
    
    def read_debug_info(self):
        
        self.file_buffer.seek(self.header.debugInfoOffset)
        
        self.debug_info_header = self.get_debug_info_header_reader()()
        self.file_buffer.readinto(self.debug_info_header)
        
        reader = self.get_offset_length_pair_reader()
        self.debug_string_table = (reader * self.debug_info_header.filename_count)()
        self.file_buffer.readinto(self.debug_string_table)
        
        self.debug_string_storage = BytesIO(self.file_buffer.read(self.debug_info_header.filename_storage_size))
        
        reader = self.get_debug_file_region_reader()
        self.debug_file_regions = (reader * self.debug_info_header.file_region_count)()
        self.file_buffer.readinto(self.debug_file_regions)
        
        if self.header.version < 91:
            sources_data_size = self.debug_info_header.lexical_data_offset
            lexical_data_size = self.debug_info_header.debug_data_size - self.debug_info_header.lexical_data_offset
            
            self.sources_data_storage = BytesIO(self.file_buffer.read(sources_data_size))
            self.lexical_data_storage = BytesIO(self.file_buffer.read(lexical_data_size))
        else:
            sources_data_size = self.debug_info_header.lexical_data_offset
            lexical_data_size = self.debug_info_header.textified_data_offset - self.debug_info_header.lexical_data_offset
            textified_data_size = self.debug_info_header.string_table_offset - self.debug_info_header.textified_data_offset
            string_table_size = self.debug_info_header.debug_data_size - self.debug_info_header.string_table_offset
            
            self.sources_data_storage = BytesIO(self.file_buffer.read(sources_data_size))
            self.lexical_data_storage = BytesIO(self.file_buffer.read(lexical_data_size))
            
            self.textified_data_storage = BytesIO(self.file_buffer.read(textified_data_size))
            self.string_table_storage = BytesIO(self.file_buffer.read(string_table_size))
        
        # TODO: Improve debug information parsing with recent versions
        # of Hermes (bytecode versions >= 91)?

    def read_whole_file(self, file_buffer : BufferedReader):
        
        # Note: the structure of the bytecode file was
        # very different before version 0.0.3, the
        # order of the segments was not the same and
        # the padding/alignment logic was different too:
        # https://github.com/facebook/hermes/blob/v0.0.2/lib/BCGen/HBC/BytecodeDataProvider.cpp#L140
        
        # This was pre-public release of Hermes (Hermes was
        # announced with version 0.1.0 in July 2019:
        # https://engineering.fb.com/2019/07/12/android/hermes/
        # and is the default engine for React Native applications
        # since September 2022, or version 0.12.0:
        # https://reactnative.dev/blog/2022/09/05/version-070#hermes-as-default-engine)
        
        self.file_buffer = file_buffer
        
        self.read_header_from_buffer() # Defines self.header
        
        self.read_functions() # Defines self.function_headers
        
        self.read_string_kinds() # Defines self.string_kinds
        
        self.read_identifier_hashes() # Defines self.identifier_hashes
        
        self.read_small_string_table() # Defines self.small_string_table
        
        self.read_overflow_string_table() # Defines self.overflow_string_table
        
        self.read_string_storage() # Defines self.string_storage and self.strings
        
        self.read_arrays() # Defines self.arrays, self.object_keys, self.object_values
        
        self.bigint_values = []
        if self.header.version >= 87:
            self.read_bigints() # Defines self.bigint_table and self.bigint_storage
        
        self.read_regexp() # Defines self.regexp_table and self.regexp_storage
        
        self.read_cjs_modules() # Defines self.cjs_modules
        
        if self.header.version >= 84:
            self.read_function_sources() # Defines self.function_sources
        
        self.read_debug_info() # Defines self.debug_info_header, self.debug_string_table, ...
        
        pass

if __name__ == '__main__':
    
    args = ArgumentParser()
    
    args.add_argument('input_file')
    
    args = args.parse_args()
    
    with open(args.input_file, 'rb') as file_descriptor:
    # with open(ASSETS_DIR + '/index.android.bundle', 'rb') as file_descriptor:

        hbc_reader = HBCReader()

        hbc_reader.read_whole_file(file_descriptor)

        pretty_print_structure(hbc_reader.header)
        
        """
        for function_header in hbc_reader.function_headers:
            pretty_print_structure(function_header)
            
            # Safety checks:
            assert function_header.unused == 0 and function_header.paramCount < 100
        """
        
        """
        # Disabled, we'll print it with strings now:
        for string_kind in hbc_reader.string_kinds:
            pretty_print_structure(string_kind)
        
        print()
        for identifier_count, identifier_hash in enumerate(hbc_reader.identifier_hashes):
            print('Identifier hash #%d: 0x%08x' % (
                identifier_count,
                identifier_hash
            ))
        print()
        
        for string in hbc_reader.small_string_table:
            pretty_print_structure(string)
        
        for overflow_string in hbc_reader.overflow_string_table:
            pretty_print_structure(overflow_string)
        """
        
        print()
        for string_kind, string in zip(hbc_reader.string_kinds, hbc_reader.strings):
            print('=> %s: %s ' % (string_kind, repr(string)))
        
        for function_count, function_header in enumerate(hbc_reader.function_headers):
            # pretty_print_structure(function_header)
            print('=> [Function #%d %s of %d bytes]: %d params @ offset 0x%08x' % (
                
                function_count,
                hbc_reader.strings[function_header.functionName],
                function_header.bytecodeSizeInBytes,
                function_header.paramCount,
                function_header.offset))
            
            # Safety checks:
            assert function_header.unused == 0 and function_header.paramCount < 100
        
        # Comment, huge (and outdated)
        
        """
        print()
        for (arr_type, array) in [
            ('Array', hbc_reader.arrays),
            ('Object key', hbc_reader.object_keys),
            ('Object value', hbc_reader.object_values)
        ]:
            
            print()
            for item_count, item in enumerate(array.items):
                if item.tag_type in (TagType.LongStringTag, TagType.ShortStringTag, TagType.ByteStringTag):
                    print('[i] %s #%d of %s: %r' % (arr_type, item_count, item.tag_type, [(
                        hbc_reader.string_kinds[value],
                        hbc_reader.strings[value]
                    ) for value in item.values]))
                else:
                    print('[i] %s #%d of %s: %r' % (arr_type, item_count, item.tag_type, item.values))
        """
        
        print()
        print('=> BigInts:')
        for bigint in hbc_reader.bigint_values:
            print('=> BigInt:', bigint)

        print()
        for regexp_count, regexp in enumerate(hbc_reader.regexp_table):
            hbc_reader.regexp_storage.seek(regexp.offset)
            regexp_data = hbc_reader.regexp_storage.read(regexp.length)
            print('=> Regexp #%d: %s' % (regexp_count, regexp_data.hex()))
            print('  => Decompiled: ', decompile_regex(parse_regex(hbc_reader.header.version, BytesIO(regexp_data))))
        
        print()
        for cjs_module_count, cjs_module in enumerate(hbc_reader.cjs_modules):
            print("=> CommonJS module #%d: %s @ %08x" % (cjs_module_count,
                cjs_module.symbol_id,
                cjs_module.offset
            ))
        
        if getattr(hbc_reader, 'function_sources', None):
            for function_source_count, function_source in enumerate(hbc_reader.function_sources):
                print("=> Function source #%d: functionId %d = string @ %08x" % (function_source_count,
                    function_source.function_id,
                    function_source.string_id
                ))
        
        print()
        print('=> Debug data:')
        pretty_print_structure(hbc_reader.debug_info_header)
        for item in hbc_reader.debug_string_table:
            pretty_print_structure(item)
        print(hbc_reader.debug_string_storage.getvalue())
        for item in hbc_reader.debug_file_regions:
            pretty_print_structure(item)

        hbc_reader.sources_data_storage.seek(0)
        print_debug_info(hbc_reader.sources_data_storage)

        print('  => Sources data:', hbc_reader.sources_data_storage.getvalue().hex())
        print('  => Lexical raw data:', hbc_reader.lexical_data_storage.getvalue().hex())
        if hbc_reader.header.version >= 91:
            print('  => Textified data:', hbc_reader.textified_data_storage.getvalue().hex())
            print('  => Raw variables and callees data:', hbc_reader.string_table_storage.getvalue().hex())

