#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Sequence, Tuple, Dict, Set, Union, Optional
from os.path import dirname, realpath, exists, join
from os import getpid, unlink, kill
from tempfile import gettempdir
from datetime import datetime
from json import load, dump
from logging import warning
from random import randint
from bisect import bisect
from signal import SIGINT
from sys import path
import platform

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

GUI_DIR = realpath(dirname(__file__))
SRC_DIR = realpath(GUI_DIR + '/..')
PARSERS_DIR = realpath(SRC_DIR + '/parsers')
HBC_OPCODES_DIR = realpath(PARSERS_DIR + '/hbc_opcodes')

from index_db import Base, DatabaseMetadataBlock, XREF_DB_FORMAT_VERSION, \
    FunctionStringXRef, FunctionFunctionXRef, FunctionBuiltinXRef

path.insert(0, PARSERS_DIR)

from serialized_literal_parser import unpack_slp_array, SLPArray, SLPValue, TagType
from hbc_bytecode_parser import parse_hbc_bytecode
from hbc_file_parser import HBCReader

path.insert(0, HBC_OPCODES_DIR)

from def_classes import Instruction, Operand, OperandMeaning

"""
    This class shall allow to store SQLite-backed data allowing
    to search for string list/function list fast within the
    hermes-dec web UI, and to search through this in-memory
    data.

    
    Such an index will carry information over both the list of strings contained in the .HBC
    bytecode file and for the corresponding list of functions.

"""

class IndexerSubprocessSocketClient:

    xx

class IndexerSubprocessSocketServer:

    def __init__(self):

        XX create_datagram_endpoint

        xx

LOCK_FILE_PATH = join(gettempdir(), 'hermes_dec_runfile.jso')

class IndexerSubprocessLockFileServer:

class IndexerSubprocessLockFileClient:

    # This methods creates the lock file if it
    # doesn't exists, killing any leftover
    # process if required.

    # Please see the "docs/GUI index worker socket
    # comm.md" file for documentation about this
    # class.

    def __init__(self):

        lock_file_exists = exists(LOCK_FILE_PATH)

        # Handle any leftover lock file

        if lock_file_exists:
            with open(LOCK_FILE_PATH) as fd:
                existing_json = load(fd)

            if existing_json['main_worker_pid'] != getpid():
                try:
                    kill(existing_json['main_worker_pid'], SIGINT)
                    warning('Killing existing server process: %d' % existing_json['main_worker_pid'])
                except Exception:
                    pass

                if (isinstance(existing_json['main_worker_port'], str) and
                    exists(existing_json['main_worker_port'])):
                    unlink(existing_json['main_worker_port'])

                for worker in existing_json.get('index_workers', []):
                    try:
                        kill(worker['pid'], SIGINT)
                    except Exception:
                        pass

                    if (isinstance(worker['port'], str) and
                        exists(worker['port'])):
                        unlink(worker['port'])
            else:
                return

        has_unix_sockets = platform.system() in ('Linux', 'Darwin')

        if has_unix_sockets:
            server_port = join(gettempdir(), 'hermes_dec_%d.sock' % getpid())
        else:
            MIN_PORT_RANGE = 40000
            MAX_PORT_RANGE = 59999
            server_port = randint(MIN_PORT_RANGE, MAX_PORT_RANGE)        

        initial_contents = {
            'main_worker_pid': getpid(),
            'main_worker_port': server_port,
            'index_workers': []
        }

        # Write the lock file

        with open(LOCK_FILE_PATH, 'w') as fd:
            dump(initial_contents, fd)

        # TODO also kill this process atexit()

        
        XX

class IndexerSubprocess:

    def __init__(self):

        # TODO - Check for lock file

        IndexerSubprocessLockFileClient(XX)

        # --> Next point

        # TODO - Spawn subprocess

        # TODO - Open UDP communication in
        # another thread

        # TODO - Return a communication queue from the caller
        # With a loop here also looking for timeouts


class Indexer:

    def __init__(self, reader : HBCReader, dir_path : str):

        self.reader = reader
        self.file_path = dir_path + '/database.sqlite3'

        self.engine = create_engine('sqlite:///' + realpath(self.file_path))
        self.Session = sessionmaker(self.engine)

        Base.metadata.create_all(bind = self.engine)

        self.indexate_in_memory()
        self.indexate_xrefs()
    
    def indexate_xrefs(self):
        with self.Session() as session:
            meta_block = session.query(DatabaseMetadataBlock).first()
            if not meta_block or meta_block.database_format < XREF_DB_FORMAT_VERSION:
                DatabaseMetadataBlock.__table__.drop(self.engine)
                Base.metadata.create_all(bind = self.engine)
                # Register cross-reference from all across the file:
                for function_count, function_header in enumerate(self.reader.function_headers):
                    for insn in parse_hbc_bytecode(function_header, self.reader):
                        for operand_index, operand in enumerate(insn.inst.operands):
                            if operand.operand_meaning:
                                operand_value = getattr(insn, 'arg%d' % (operand_index + 1), None)
                                if operand_value is not None:
                                    if operand.operand_meaning == OperandMeaning.string_id:
                                        # self.hbc_reader.strings[operand_value]
                                        session.add(
                                            FunctionStringXRef(
                                                ref_string_id = operand_value,
                                                function_id = function_count,
                                                insn_original_pos = insn.original_pos,
                                                insn_operand_idx = operand_index
                                            )
                                        )
                                    elif operand.operand_meaning == OperandMeaning.function_id:
                                        session.add(
                                            FunctionFunctionXRef(
                                                ref_function_id = operand_value,
                                                function_id = function_count,
                                                insn_original_pos = insn.original_pos,
                                                insn_operand_idx = operand_index
                                            )
                                        )
                                
                        if insn.inst.name in ('NewArrayWithBuffer', 'NewArrayWithBufferLong'):
                            for item in unpack_slp_array(self.reader.arrays[insn.arg4:], insn.arg3).items:
                                if item.tag_type in (TagType.LongStringTag,
                                        TagType.ShortStringTag, TagType.ByteStringTag):
                                    session.add(
                                        FunctionStringXRef(
                                            ref_string_id = item.value,
                                            function_id = function_count,
                                            insn_original_pos = insn.original_pos,
                                            insn_operand_idx = 4
                                        )
                                    )
                        elif insn.inst.name in ('NewObjectWithBuffer', 'NewObjectWithBufferLong'):
                            for item in unpack_slp_array(self.reader.object_keys[insn.arg4:], insn.arg3).items:
                                if item.tag_type in (TagType.LongStringTag,
                                        TagType.ShortStringTag, TagType.ByteStringTag):
                                    session.add(
                                        FunctionStringXRef(
                                            ref_string_id = item.value,
                                            function_id = function_count,
                                            insn_original_pos = insn.original_pos,
                                            insn_operand_idx = 4
                                        )
                                    )
                            for item in unpack_slp_array(self.reader.object_values[insn.arg5:], insn.arg3).items:
                                if item.tag_type in (TagType.LongStringTag,
                                        TagType.ShortStringTag, TagType.ByteStringTag):
                                    session.add(
                                        FunctionStringXRef(
                                            ref_string_id = item.value,
                                            function_id = function_count,
                                            insn_original_pos = insn.original_pos,
                                            insn_operand_idx = 5
                                        )
                                    )
                        elif insn.inst.name in ('CallBuiltin', 'CallBuiltinLong', 'GetBuiltinClosure'):
                            builtin_number = insn.arg2
                            session.add(
                                FunctionBuiltinXRef(
                                    ref_builtin_id = operand_value,
                                    function_id = function_count,
                                    insn_original_pos = insn.original_pos,
                                    insn_operand_idx = 2
                                )
                            )
            
                # Create a metadata block for the whole file:
                session.add(
                    DatabaseMetadataBlock(
                        database_format = XREF_DB_FORMAT_VERSION,
                        creation_time = datetime.now(),
                        modification_time = datetime.now(),
                        last_open_time = datetime.now()
                    )
                )
            else:
                meta_block.last_open_time = datetime.now()
            session.commit()

    
    def indexate_in_memory(self):
        self.raw_strings_blob = ''
        self.raw_strings_indexes : List[int] = []
        for string in self.reader.strings:
            self.raw_strings_indexes.append(len(self.raw_strings_blob))
            self.raw_strings_blob += string.lower() + '\x00'

        self.raw_functions_blob = ''
        self.raw_functions_indexes : List[int] = []
        for function_header in self.reader.function_headers:
            self.raw_functions_indexes.append(len(self.raw_functions_blob))
            raw_func_name = self.reader.strings[function_header.functionName]
            self.raw_functions_blob += raw_func_name.lower() + '\x00' + '%08x' % function_header.offset + '\x00'
    
    # Return a list of possible string IDs from a given
    # searched substring
    def find_strings_from_substring(self, token : str) -> str:

        string_ids : Set[str] = set()

        haystack = token.lower()
        pos = 0
        while True:
            needle = self.raw_strings_blob.find(haystack, pos)
            if needle == -1:
                break
            string_id = bisect(self.raw_strings_indexes, needle) - 1
            pos = needle + len(token)
            
            string_ids.add(string_id)

        return sorted(string_ids)

    # Return a list of possible function IDs from a given
    # searched string, which may either represent a
    # raw hex function address or a function name
    def find_functions_from_substring(self, token : str) -> List[int]:

        function_ids : Set[int] = set()

        assert token
        haystackes = {token.lower()}

        try:
            haystackes.add('%08x' % int(token, 16))
        except ValueError:
            pass

        for haystack in sorted(haystackes):
            pos = 0
            while True:
                needle = self.raw_functions_blob.find(haystack, pos)
                if needle == -1:
                    break
                function_id = bisect(self.raw_functions_indexes, needle) - 1
                pos = needle + len(token)
                
                function_ids.add(function_id)
        
        return sorted(function_ids)
