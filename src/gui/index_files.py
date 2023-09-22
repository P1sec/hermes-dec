#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Sequence, Tuple, Dict, Set, Union, Optional
from os.path import dirname, realpath
from bisect import bisect
from sys import path

from sqlalchemy import create_engine, Column, Text, Integer, Boolean, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session

GUI_DIR = realpath(dirname(__file__))
SRC_DIR = realpath(GUI_DIR + '/..')
PARSERS_DIR = realpath(SRC_DIR + '/parsers')

path.insert(0, PARSERS_DIR)

from hbc_bytecode_parser import parse_hbc_bytecode
from hbc_file_parser import HBCReader

"""
    This class shall allow to store SQLite-backed data allowing
    to search for string list/function list fast within the
    hermes-dec web UI, and to search through this in-memory
    data.

    
    Such an index will carry information over both the list of strings contained in the .HBC
    bytecode file and for the corresponding list of functions.

"""

Base = declarative_base()

class BaseFunctionXRef(Base):
    __tablename__ = 'function_x_ref'
    #WIP ..

    id = Column(Integer, primary_key = True)

    function_id = Column(Integer, index = True)

    type = Column(String)
    insn_original_pos = Column(Integer)
    insn_operand_idx = Column(Integer)

    __mapper_args__ = {
        'polymorphic_on': 'type'
    }

class FunctionStringXRef(BaseFunctionXRef):
    ref_string_id = Column(Integer, index = True)

    __mapper_args__ = {
        'polymorphic_identity': 'string'
    }

class FunctionFunctionXRef(BaseFunctionXRef):
    ref_function_id = Column(Integer, index = True)

    __mapper_args__ = {
        'polymorphic_identity': 'function'
    }


class Indexer:

    def __init__(self, reader : HBCReader, dir_path : str):

        self.reader = reader
        self.file_path = dir_path + '/database.sqlite3'

        """
        # Impl. later:
        self.engine = create_engine('sqlite://' + realpath(file_path))
        self.Session = Session(engine)

        Base.metadata.create_all(bind = self.engine)
        """

        self.indexate_in_memory()
    
    """
    # Impl. later:
    def indexate_xrefs(self):
        for function_count, function_header in enumerate(self.reader.function_headers):
            for instruction in parse_hbc_bytecode(function_header, self.reader):
                X
    """

    
    def indexate_in_memory(self):
        """
        self.raw_strings_blob = ''
        self.raw_strings_indexes : List[int] = []
        for string in self.reader.strings:
            self.raw_strings_indexes.append(len(self.raw_string_blob))
            self.raw_strings_blob += string + '\x00'
        """

        self.raw_functions_blob = ''
        self.raw_functions_indexes : List[int] = []
        for function_header in self.reader.function_headers:
            self.raw_functions_indexes.append(len(self.raw_functions_blob))
            raw_func_name = self.reader.strings[function_header.functionName]
            self.raw_functions_blob += raw_func_name + '\x00' + '%08x' % function_header.offset + '\x00'
    
    # Return a list of possible function IDs from a given
    # searched string, which may either represent a
    # raw hex function address or a function name
    def find_functions_from_substring(self, token : str) -> List[int]:

        function_ids : Set[int] = set()

        assert token
        haystackes = {token}

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

    # XXX WIP