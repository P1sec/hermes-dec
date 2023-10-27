#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from asyncio import Future, run, get_running_loop, create_task, create_subprocess_exec
from typing import Dict, Set, List, Sequence, Optional, Tuple
from websockets import serve, WebSocketServerProtocol
from websockets.exceptions import ConnectionClosed
from os.path import dirname, realpath
from subprocess import PIPE, DEVNULL
from json import loads, dumps
from threading import Thread
from asyncio import wait_for
from sys import path
import sys

GUI_DIR = realpath(dirname(__file__))
INDEX_WORKER_DIR = realpath(GUI_DIR + '/index_worker')
SRC_DIR = realpath(GUI_DIR + '/..')
DECOMPILATION_DIR = realpath(SRC_DIR + '/decompilation')
PARSERS_DIR = realpath(SRC_DIR + '/parsers')

path.insert(0, INDEX_WORKER_DIR)
path.insert(0, DECOMPILATION_DIR)
path.insert(0, GUI_DIR)

from index_files import INDEXER_ENTRY_SCRIPT, MemoryIndex, DatabaseIndexReader
from paginated_table import RAW_TABLE_MODEL_NAME_TO_OBJ
from project_meta import ProjectSubdirManager
from pre_render_graph import draw_stuff

from defs import HermesDecompiler, DecompiledFunctionBody
from pass1_set_metadata import pass1_set_metadata
from pass1b_make_basic_blocks import pass1b_make_basic_blocks
from pass1c_visit_code_paths import pass1c_visit_code_paths

path.insert(0, PARSERS_DIR)

from hbc_bytecode_parser import parse_hbc_bytecode
from hbc_file_parser import HBCReader

class WebsocketClient:

    reader : HBCReader
    project : ProjectSubdirManager
    socket : WebSocketServerProtocol

    def __init__(self, socket : WebSocketServerProtocol):
        self.socket = socket

    def has_hash(self, file_hash : str):
        return ProjectSubdirManager.has_hash(file_hash)
    
    def open_by_hash(self, file_hash : str):
        self.project = ProjectSubdirManager.open_by_hash(file_hash)

    def create_file(self, file_name : str):
        self.project = ProjectSubdirManager.new_with_name(file_name)
    
    def write_to_file(self, bytes_slice : bytes):
        self.project.write_to_file(bytes_slice)
    
    def parse_file(self):
        self.reader = HBCReader()

        self.project.save_to_disk()

        self.reader.read_whole_file(self.project.file_buffer)
        self.project.write_or_update_metadata({
            'bytecode_version': self.reader.header.version
        })
    
    async def monitor_subprocess_stderr(self, child):

        while True:
            try:
                data = (await child.stderr.readline()).decode('utf-8')
            except BrokenPipeError:
                break
            if not data:
                break

            await self.socket.send(dumps({
                'type': 'console_error_log',
                'data': data
            }))
    
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

                await self.socket.send(dumps({
                    'type': 'console_log',
                    'data': raw_message
                }))
            
            elif data['type'] == 'indexing_status_log':

                await self.socket.send(dumps({
                    'type': 'console_log',
                    'data': data['message']
                }))
        
        status_code = await wait_for(child.wait(), 60)

        if status_code == 0:
            await self.socket.send(dumps({
                'type': 'console_log',
                'data': '(Indexer worker finished correctly.)\n'
            }))
        else:
            await self.socket.send(dumps({
                'type': 'console_error_log',
                'data': '(Indexer worker exited with status: %d)\n' % status_code
            }))
    
    async def launch_index_subprocess_task(self):

        PIPE_BUFFER_SIZE = 20 * 1024 * 1024
        
        child = await create_subprocess_exec(sys.executable,
            INDEXER_ENTRY_SCRIPT,
            self.project.subdir_path,
            self.project.file_buffer.name,
            stdin = PIPE, # This pipe is just for having a thread in the child
                # process that have it interrupt on parent death (e.g. SIGKILL received)
            stdout = PIPE,
            stderr = PIPE,
            limit = PIPE_BUFFER_SIZE)

        create_task(self.monitor_subprocess_stderr(child))
        create_task(self.monitor_subprocess_stdout_or_exit(child))

    async def spawn_indexer(self):
        
        await self.launch_index_subprocess_task()

        self.database_index = DatabaseIndexReader(self.reader, self.project.subdir_path)

        self.memory_index = await get_running_loop().run_in_executor(None, MemoryIndex, self.reader)

        #     XX DO BACK STATE UPDATE HERE

    def get_metadata(self) -> dict:

        return {
            'file_metadata': self.project.read_metadata()
        }

    async def handle(self):
        
        loop = get_running_loop()

        await self.socket.send(dumps({
            'type': 'recent_files',
            **ProjectSubdirManager.get_recent_files_data()
        }))

        async for msg in self.socket:
            # Receive the next message.

            if type(msg) == bytes:

                self.write_to_file(msg)
            
            else:
                
                msg = loads(msg)

                print('DEBUG: Received: ', msg)

                msg_type = msg['type']

                # Please see the "../../../docs/GUI server websocket protocol.md"
                # file for documentation about the following messages.

                if msg_type == 'open_file_by_hash':

                    if self.has_hash(msg['hash']):
                        self.open_by_hash(msg['hash'])

                        await loop.run_in_executor(None, self.parse_file)
                        await self.spawn_indexer()

                        await self.socket.send(dumps({
                            'type': 'file_opened',
                            **self.get_metadata()
                        }))
                    else:
                        await self.socket.send(dumps({
                            'type': 'file_hash_unknown'
                        }))

                elif msg_type == 'begin_transfer':
                
                    self.create_file(msg['file_name'])

                elif msg_type == 'end_transfer':

                    await loop.run_in_executor(None, self.parse_file)
                    await self.spawn_indexer()

                    await self.socket.send(dumps({
                        'type': 'file_opened',
                        **self.get_metadata()
                    }))

                    await self.socket.send(dumps({
                        'type': 'recent_files',
                        **ProjectSubdirManager.get_recent_files_data()
                    }))

                elif msg_type == 'get_table_data':

                    table_name = msg['table']

                    if table_name not in RAW_TABLE_MODEL_NAME_TO_OBJ:
                        raise NotImplementedError('[!] Unimplemented table model: %s' % table_name)

                    table_model = RAW_TABLE_MODEL_NAME_TO_OBJ[table_name]()

                    await self.socket.send(dumps({
                        'type': 'table_data',
                        **table_model.get_json_response(
                            server_connection = self,
                            current_row_idx = msg.get('current_row'),
                            current_page_if_not_current_row = msg.get('page'),
                            search_query = msg.get('text_filter')
                        )
                    }))
            
                elif msg_type == 'analyze_function':

                    # - Internally disassemble the queried function.

                    function_header = self.reader.function_headers[msg['function_id']]

                    instructions = list(parse_hbc_bytecode(function_header, self.reader))

                    # - Use code from the decompilation module in order to
                    #   construct the graph structures that will be used to
                    #   pre-render/display the in-browser on-screen graph.

                    state = HermesDecompiler()
                    state.hbc_reader = self.reader
                    state.function_header = function_header

                    dehydrated = DecompiledFunctionBody()

                    dehydrated.function_id = msg['function_id']
                    dehydrated.function_object = function_header
                    dehydrated.is_global = msg['function_id'] == self.reader.header.globalCodeIndex

                    if dehydrated.function_object.hasExceptionHandler:
                        dehydrated.exc_handlers = self.reader.function_id_to_exc_handlers[msg['function_id']]

                    pass1_set_metadata(state, dehydrated)
                    pass1b_make_basic_blocks(state, dehydrated)
                    # pass1c_visit_code_paths(state, dehydrated) # Commented right now

                    # - Return the resulting pre-rendered/displayed graph as
                    #   serialized JSON. (WIP...)

                    await self.socket.send(dumps(draw_stuff(instructions, dehydrated)))

                    # WIP ..

                # elif msg_type == 'XX SEE. MD DOC':
                    # XX

                # await websocket.send(message)


class WebsocketServer:

    async def handle_ws_client(self, socket):
        connection = WebsocketClient(socket)

        await connection.handle()

async def async_main():
    # TODO: Use a process (or thread but think of GIL) pool?
    # TODO: Implement the client/server communication defined within the
    # "docs/GUI server websocket protocol.md" file, as well as the GUI

    socket_server = WebsocketServer()
    async with serve(socket_server.handle_ws_client, 'localhost', 49594):
        await Future()  # run forever

def main():
    run(async_main())

if __name__ == '__main__':
    main()