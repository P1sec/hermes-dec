#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import Optional, Any, List, Dict, Set, Union, Sequence
from os.path import join, dirname, realpath, exists, getsize
from os import makedirs, readlink, symlink, listdir
from appdirs import user_data_dir
from unidecode import unidecode
from datetime import datetime
from json import load, dump
from hashlib import sha256
from shutil import rmtree
from sys import path
from re import sub

GUI_DIR = realpath(dirname(__file__))
SRC_DIR = realpath(GUI_DIR + '/..')
PARSERS_DIR = realpath(SRC_DIR + '/parsers')

path.insert(0, PARSERS_DIR)

from hbc_file_parser import HBCReader

"""
    TODO :

    Create the following folders:
        ./by-hash/<sha256> -> symlink to /by-date/<timestamp>-<slugified-name>
        ./by-date/<timestamp>-<slugified-name> -> actual contents containing
            "index.android.bundle" and "metadata.json" files
    
    TODO : Also support parsing and extraing APK files, set appropriate metadata
    onto .JSON files, etc.

    TODO : Create a "Recent files" list based off the JSON metadata

    TODO : Improve JS/Python error-handling client-side in the web UI etc.
"""

LOCAL_SHARE_PATH = user_data_dir('HermesDec', 'P1Security')

BY_HASH_PATH = join(LOCAL_SHARE_PATH, 'by-hash')
BY_DATE_PATH = join(LOCAL_SHARE_PATH, 'by-date')


class ProjectSubdirManager:

    @classmethod
    def new_with_name(cls, name : str):

        self = cls()
        self.orig_name = name
        dirname = self.gen_unique_dirname(name)

        self.subdir_path = join(BY_DATE_PATH, dirname)

        makedirs(self.subdir_path, exist_ok = True)

        self.file_buffer = open(self.subdir_path + '/index.android.bundle', 'wb+')
        self.metadata_path = join(self.subdir_path, 'metadata.json')
        self.sha_state = sha256()

        return self
    
    @staticmethod
    def has_hash(file_hash : str):
        return exists(join(BY_HASH_PATH, file_hash))
    
    @staticmethod
    def get_recent_files_data() -> dict:

        recent_files = []

        if exists(BY_DATE_PATH):
            for file_entry in reversed(sorted(listdir(BY_DATE_PATH))):

                project = ProjectSubdirManager.open_by_path(join(BY_DATE_PATH, file_entry))
                recent_files.append(project.read_metadata())

        return {
            'recent_files': recent_files
        }
    
    @classmethod
    def open_by_hash(cls, file_hash):
        return cls.open_by_path(readlink(join(BY_HASH_PATH, file_hash)))

    @classmethod
    def open_by_path(cls, path):
        self = cls()
        self.subdir_path = path

        self.file_buffer = open(self.subdir_path + '/index.android.bundle', 'rb')
        self.metadata_path = join(self.subdir_path, 'metadata.json')

        return self
    
    def write_to_file(self, data : bytes):

        self.file_buffer.write(data)
        self.sha_state.update(data)
    
    def write_or_update_metadata(self, extra_args = {}):

        if exists(self.metadata_path):
            with open(self.metadata_path) as fd:
                json_data = load(fd)
        else:
            json_data = {
                'orig_name': self.orig_name,
                'file_hash': self.sha_state.hexdigest(),
                'file_size': getsize(self.file_buffer.name),
                'db_created_time': datetime.now().isoformat(),
                'raw_disk_path': self.file_buffer.name,
                'dir_disk_path': self.subdir_path
            }
        
        json_data['db_updated_time'] = datetime.now().isoformat()

        json_data.update(extra_args)
        
        with open(self.metadata_path, 'w') as fd:
            dump(json_data, fd, indent = 4)
            fd.write('\n')
    
    def read_metadata(self) -> dict:
        with open(self.metadata_path) as fd:
            return load(fd)
    
    def save_to_disk(self):
        
        self.file_buffer.flush()
        self.file_buffer.seek(0)

        self.write_or_update_metadata()

        if hasattr(self, 'sha_state'):
            hash_path = join(BY_HASH_PATH, self.sha_state.hexdigest())

            if not exists(hash_path):
                makedirs(BY_HASH_PATH, exist_ok = True)
                symlink(self.subdir_path, hash_path)
    
    def gen_unique_dirname(self, orig_name : str):

        return '-'.join(filter(None, [
            datetime.now().isoformat().split('.')[0],
            sub('[^a-z0-9\-]', '', sub('\s+', '-', unidecode(orig_name).lower().strip()))
        ]))



