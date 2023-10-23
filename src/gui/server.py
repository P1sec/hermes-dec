#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from websockets.exceptions import ConnectionClosed
from asyncio import Future, run, get_running_loop
from os.path import dirname, realpath
from json import loads, dumps
from websockets import serve
from threading import Thread
from asyncio import Queue
from sys import path

GUI_DIR = realpath(dirname(__file__))
INDEX_WORKER_DIR = realpath(GUI_DIR + '/index_workers')
SRC_DIR = realpath(GUI_DIR + '/..')
DECOMPILATION_DIR = realpath(SRC_DIR + '/decompilation')
PARSERS_DIR = realpath(SRC_DIR + '/parsers')

path.insert(0, INDEX_WORKER_DIRS)
path.insert(0, DECOMPILATION_DIR)
path.insert(0, GUI_DIR)

from paginated_table import RAW_TABLE_MODEL_NAME_TO_OBJ
from index_files import Indexer, IndexerSubprocess
from project_meta import ProjectSubdirManager
from pre_render_graph import draw_stuff

from defs import HermesDecompiler, DecompiledFunctionBody
from pass1_set_metadata import pass1_set_metadata
from pass1b_make_basic_blocks import pass1b_make_basic_blocks
from pass1c_visit_code_paths import pass1c_visit_code_paths

from index_files import IndexerSubprocessLockFileClient

path.insert(0, PARSERS_DIR)

from hbc_bytecode_parser import parse_hbc_bytecode
from hbc_file_parser import HBCReader

queue = asyncio.Queue()

class WebsocketClient:

    reader : HBCReader
    project : ProjectSubdirManager

    def has_hash(self, file_hash : str):
        return ProjectSubdirManager.has_hash(file_hash)
    
    def open_by_hash(self, file_hash : str):
        self.project = ProjectSubdirManager.open_by_hash(file_hash)

    def create_file(self, file_name : str):
        self.project = ProjectSubdirManager.new_with_name(file_name)
    
    def write_to_file(self, bytes_slice : bytes):
        self.project.write_to_file(bytes_slice)
    
    def parse_file(self, TODO_PASS_AN_ASYNCIO_SIGNAL_QUEUE):
        self.reader = HBCReader()

        # TODO_USE_THE_ASYNCIO_SIGNAL_QUEUE_HERE
        #  _TO_BE_DWINDLED_WITH_THE_SOCKET_
        #  _MESSAGE_RECEIVER_LOOP

        self.project.save_to_disk()

        self.reader.read_whole_file(self.project.file_buffer)
        self.project.write_or_update_metadata({
            'bytecode_version': self.reader.header.version
        })

        # WIP --
        self.search_index = IndexerSubprocess(self.reader, self.project.subdir_path)

        # XXXXXX
            =)
        
        self.search_index_communicator_queue_XX = self.search_index_XXX
    
    def get_metadata(self) -> dict:

        return {
            'file_metadata': self.project.read_metadata()
        }

class WebsocketServer:

    async def __init__(self):

        XX_INSTANTIATE_IndexerSubprocessLockFileClient
        
        XX_AT_EXIT_CLOSE_SOCKETS_REMOVE_LOCK_FILE

    async def handle_ws_client(socket):
        loop = get_running_loop()
        connection = WebsocketClient()

        await socket.send(dumps({
            'type': 'recent_files',
            **ProjectSubdirManager.get_recent_files_data()
        }))

        # TODO
        # Implement some kind of select()
        # here from thread-multiprocess issued
        # messages from the indexing part

        # -(---> TODO NEXT)
        -> XX TODO READ WEBSOCKETS.(API REF).RECV DOCS
        #    ( PIN THE CORRESPONDING TAB )
        # (https://websockets.readthedocs.io/en/stable/reference/asyncio/server.html
        # )

        while True:
            # Receive the next message.

            XX_OTHER_TASK_QUEUE_OBJ = OBTAIN_QUEUE_FROM_OTHER_TASK

            # -> TODO READ https://docs.python.org/3/library/asyncio-task.html#asyncio.wait_for
            # -> TODO READ https://docs.python.org/3/library/asyncio-task.html#waiting-primitives
            XX_FROM_ASYNCIO_IMPORT_QUEUE
            
            XX_USE_WAIT_FOR([SOCKET_OBJ, OTHER_TASK_QUEUE_OBJ], ANY_OF_THESE)

            try:
                msg = await socket.recv()
            
            except ConnectionClosed:
                # TODO USE ACTUAL DEBUG CALL
                print('DEBUG : CONNECTION CLOSED (TODO USE ACTUAL DEBUG CALL)')
                break

            if type(msg) == bytes:

                connection.write_to_file(msg)
            
            else:
                
                msg = loads(msg)

                print('DEBUG: Received: ', msg)

                msg_type = msg['type']

                # Please see the "../../../docs/GUI server websocket protocol.md"
                # file for documentation about the following messages.

                if msg_type == 'open_file_by_hash':

                    if connection.has_hash(msg['hash']):
                        connection.open_by_hash(msg['hash'])

                        # TODO - Redesign the event loop here =)

                        await loop.run_in_executor(None, connection.parse_file)

                        await socket.send(dumps({
                            'type': 'file_opened',
                            **connection.get_metadata()
                        }))
                    else:
                        await socket.send(dumps({
                            'type': 'file_hash_unknown'
                        }))

                elif msg_type == 'begin_transfer':
                
                    connection.create_file(msg['file_name'])

                elif msg_type == 'end_transfer':

                    await loop.run_in_executor(None, connection.parse_file)

                    await socket.send(dumps({
                        'type': 'file_opened',
                        **connection.get_metadata()
                    }))

                    await socket.send(dumps({
                        'type': 'recent_files',
                        **ProjectSubdirManager.get_recent_files_data()
                    }))

                elif msg_type == 'get_table_data':

                    table_name = msg['table']

                    if table_name not in RAW_TABLE_MODEL_NAME_TO_OBJ:
                        raise NotImplementedError('[!] Unimplemented table model: %s' % table_name)

                    table_model = RAW_TABLE_MODEL_NAME_TO_OBJ[table_name]()

                    await socket.send(dumps({
                        'type': 'table_data',
                        **table_model.get_json_response(
                            server_connection = connection,
                            current_row_idx = msg.get('current_row'),
                            current_page_if_not_current_row = msg.get('page'),
                            search_query = msg.get('text_filter')
                        )
                    }))
            
                elif msg_type == 'analyze_function':

                    # - Internally disassemble the queried function.

                    function_header = connection.reader.function_headers[msg['function_id']]

                    instructions = list(parse_hbc_bytecode(function_header, connection.reader))

                    # - Use code from the decompilation module in order to
                    #   construct the graph structures that will be used to
                    #   pre-render/display the in-browser on-screen graph.

                    state = HermesDecompiler()
                    state.hbc_reader = connection.reader
                    state.function_header = function_header

                    dehydrated = DecompiledFunctionBody()

                    dehydrated.function_id = msg['function_id']
                    dehydrated.function_object = function_header
                    dehydrated.is_global = msg['function_id'] == connection.reader.header.globalCodeIndex

                    if dehydrated.function_object.hasExceptionHandler:
                        dehydrated.exc_handlers = connection.reader.function_id_to_exc_handlers[msg['function_id']]

                    pass1_set_metadata(state, dehydrated)
                    pass1b_make_basic_blocks(state, dehydrated)
                    # pass1c_visit_code_paths(state, dehydrated) # Commented right now

                    # - Return the resulting pre-rendered/displayed graph as
                    #   serialized JSON. (WIP...)

                    await socket.send(dumps(draw_stuff(instructions, dehydrated)))

                    # WIP ..

                # elif msg_type == 'XX SEE. MD DOC':
                    # XX

                # await websocket.send(message)

async def async_main():
    # TODO: Use a process (or thread but think of GIL) pool?
    # TODO: Implement the client/server communication defined within the
    # "docs/GUI server websocket protocol.md" file, as well as the GUI

    socket_server = await WebsocketServer()
    async with serve(socket_server.handle_ws_client, 'localhost', 49594):
        await Future()  # run forever

def main():
    run(async_main())

if __name__ == '__main__':
    main()