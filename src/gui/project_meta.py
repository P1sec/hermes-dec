#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from asyncio import get_running_loop, create_task, wait_for, Lock, create_subprocess_exec
from os.path import join, dirname, realpath, basename, exists, getsize
from typing import Optional, Any, List, Dict, Set, Union, Sequence
from os import makedirs, readlink, symlink, listdir
from websockets import WebSocketServerProtocol
from json import load, dump, loads, dumps
from asyncio.subprocess import Process
from subprocess import PIPE, DEVNULL
from appdirs import user_data_dir
from unidecode import unidecode
from datetime import datetime
from hashlib import sha256
from shutil import rmtree
from sys import path
from re import sub
import sys

GUI_DIR = realpath(dirname(__file__))
INDEX_WORKER_DIR = realpath(GUI_DIR + '/index_worker')
SRC_DIR = realpath(GUI_DIR + '/..')
PARSERS_DIR = realpath(SRC_DIR + '/parsers')

path.insert(0, INDEX_WORKER_DIR)
path.insert(0, PARSERS_DIR)

from index_files import INDEXER_ENTRY_SCRIPT, MemoryIndex, DatabaseIndexReader
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

_hash_to_handle : Dict[str, 'ProjectInstanceManager'] = {}

class ProjectInstanceManager:

    file_hash : str

    web_console_backlog : List[Dict[str, str]] # List of logged "indexing_state" or "indexing_status_log" socket messages
    sockets : List[WebSocketServerProtocol] # See https://websockets.readthedocs.io/en/stable/reference/asyncio/server.html#websockets.server.WebSocketServerProtocol

    subdir_path : str
    metadata_path : str

    reader : HBCReader = None
    memory_index : MemoryIndex = None
    database_index : DatabaseIndexReader = None

    child : Process = None

    def __init__(self, file_hash : str):

        assert file_hash.isalnum() and len(file_hash) == 64

        self.file_hash = file_hash

        _hash_to_handle[file_hash] = self

        self.file_parsing_lock = Lock()

        self.web_console_backlog = []
        self.sockets = []

        self.subdir_path = realpath(join(BY_HASH_PATH, file_hash))
        self.metadata_path = join(self.subdir_path, 'metadata.json')
    
    async def register_socket(self, socket : WebSocketServerProtocol):
        if socket not in self.sockets:
            self.sockets.append(socket)
            for message in self.web_console_backlog:
                await socket.send(dumps(message))
    
    # Todo use this everywhere needed in the code:
    async def unregister_socket(self, socket : WebSocketServerProtocol):
        if socket in self.sockets:
            self.sockets.remove(socket)
            if not self.sockets and self.file_hash in _hash_to_handle:
                del _hash_to_handle[self.file_hash]
                if self.child:
                    # Closing stdin within the child should have
                    # it interrupt
                    await self.child.wait()
    
    async def broadcast_message(self, message : Dict[str, str]):
        self.web_console_backlog.append(message)
        for socket in list(self.sockets):
            await socket.send(dumps(message))

    @classmethod
    def new_with_name(cls, file_hash : str, name : str):

        self = cls(file_hash)
        datebased_name = self.gen_datebased_dirname(name)

        makedirs(join(BY_DATE_PATH, datebased_name), exist_ok = False)
        symlink(join('..', 'by-date', datebased_name), join(BY_HASH_PATH, file_hash))

        self.file_buffer = open(self.subdir_path + '/index.android.bundle', 'wb+')
        self.sha_state = sha256()

        json_data = {
            'orig_name': name,
            'file_hash': file_hash,
            'file_size': 0, # <-- File not written to disk yet
            'db_created_time': datetime.now().isoformat(),
            'raw_disk_path': self.file_buffer.name,
            'dir_disk_path': self.subdir_path,
            'db_updated_time': datetime.now().isoformat()
        }

        with open(self.metadata_path, 'w') as fd:
            dump(json_data, fd, indent = 4)
            fd.write('\n')
        
        # TODO IMPLEMENT EXTRA CORRUPTION CHECK BEFORE/AFTER TRANSFER?
    
        return self
    
    @classmethod
    def open_by_hash(cls, file_hash):
        if file_hash in _hash_to_handle:
            return _hash_to_handle[file_hash]

        self = cls(file_hash)

        self.file_buffer = open(self.subdir_path + '/index.android.bundle', 'rb')   

        return self
 
    @staticmethod
    def project_hash_exists(file_hash : str):
        return exists(join(BY_HASH_PATH, file_hash))
    
    @staticmethod
    def get_recent_files_data() -> dict:

        recent_files = []

        if exists(BY_DATE_PATH):
            for file_entry in reversed(sorted(listdir(BY_DATE_PATH))):

                meta_path = join(BY_DATE_PATH, file_entry, 'metadata.json')
                with open(meta_path) as fd:
                    recent_files.append(load(fd))

        return {
            'recent_files': recent_files
        }

    async def monitor_subprocess_stderr(self, child):

        while True:
            try:
                data = (await child.stderr.readline()).decode('utf-8')
            except BrokenPipeError:
                break
            if not data:
                break

            await self.broadcast_message({
                'type': 'console_error_log',
                'data': data
            })
    
    async def monitor_subprocess_stdout_or_exit(self, child):

        while True:
            try:
                data = (await child.stdout.readline()).decode('utf-8')
            except BrokenPipeError:
                break
            if not data:
                break
            data = loads(data.strip())
            if data['type'] == 'indexing_state':
                raw_message = {
                    'indexing_functions': 'The file is being indexed...\n',
                    'fully_indexed': 'The file has been fully indexed.\n'
                }[data['state']]

                # XX Handle fully indexed state?

                await self.broadcast_message({
                    'type': 'console_log',
                    'data': raw_message
                })
            
            elif data['type'] == 'indexing_status_log':

                await self.broadcast_message({
                    'type': 'console_log',
                    'data': data['message']
                })
        
        status_code = await wait_for(child.wait(), 60)

        if status_code == 0:
            await self.broadcast_message({
                'type': 'console_log',
                'data': '(Indexer worker finished correctly.)\n'
            })
        else:
            await self.broadcast_message({
                'type': 'console_error_log',
                'data': '(Indexer worker exited with status: %d)\n' % status_code
            })
    
    async def launch_index_subprocess_task(self):

        PIPE_BUFFER_SIZE = 20 * 1024 * 1024
        
        self.child = await create_subprocess_exec(sys.executable,
            INDEXER_ENTRY_SCRIPT,
            self.subdir_path,
            self.file_buffer.name,
            stdin = PIPE, # This pipe is just for having a thread in the child
                # process that have it interrupt on parent death (e.g. SIGKILL received)
            stdout = PIPE,
            stderr = PIPE,
            limit = PIPE_BUFFER_SIZE)

        create_task(self.monitor_subprocess_stderr(self.child))
        create_task(self.monitor_subprocess_stdout_or_exit(self.child))

    def parse_file_blocking(self):
        self.reader = HBCReader()

        self.file_buffer.seek(0)

        self.reader.read_whole_file(self.file_buffer)
        self.write_or_update_metadata({
            'bytecode_version': self.reader.header.version
        })

        self.memory_index = MemoryIndex(self.reader)
    
    async def parse_file(self):
        # Parse file if not parsed yet, and exclusive lock
        # this function for the moment this is done.

        async with self.file_parsing_lock:

            if not self.reader:
                await get_running_loop().run_in_executor(None, self.parse_file_blocking)
                
                await self.launch_index_subprocess_task()

                self.database_index = DatabaseIndexReader(self.reader, self.subdir_path)
    
    def write_to_file(self, data : bytes):

        self.file_buffer.write(data)
        self.sha_state.update(data)
    
    def write_or_update_metadata(self, extra_args = {}):

        with open(self.metadata_path) as fd:
            json_data = load(fd)

        json_data['db_updated_time'] = datetime.now().isoformat()

        json_data.update(extra_args)
        
        with open(self.metadata_path, 'w') as fd:
            dump(json_data, fd, indent = 4)
            fd.write('\n')
    
    def read_metadata(self) -> dict:
        with open(self.metadata_path) as fd:
            return load(fd)
    
    def end_transfer(self):
        
        self.file_buffer.flush()
        self.file_buffer.seek(0)

        self.write_or_update_metadata({
            'file_size': getsize(self.file_buffer.name)
        })

        assert self.file_hash == self.sha_state.hexdigest()
    
    def gen_datebased_dirname(self, orig_name : str):

        return '-'.join(filter(None, [
            datetime.now().isoformat().split('.')[0],
            sub('[^a-z0-9\-]', '', sub('\s+', '-', unidecode(orig_name).lower().strip()))
        ]))



