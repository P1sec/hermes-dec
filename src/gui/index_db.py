#!/usr/bin/python3
#-*- encoding: Utf-8 -*-

from sqlalchemy import Column, Text, Integer, Boolean, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

"""
    This file contains the definition for the SQLite database
    used into the "index_files.py" module.
"""

# Increment in order to force an update of the database
# cross-reference
XREF_DB_FORMAT_VERSION = 1



Base = declarative_base()

class DatabaseMetadataBlock(Base):
    __tablename__ = 'database_metadata_block'

    # Single-row table containing the following fields:
    database_format = Column(Integer, primary_key = True)
    creation_time = Column(DateTime)
    modification_time = Column(DateTime)
    last_open_time = Column(DateTime)

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

class FunctionBuiltinXRef(BaseFunctionXRef):
    ref_builtin_id = Column(Integer, index = True)

    __mapper_args__ = {
        'polymorphic_identity': 'builtin'
    }
