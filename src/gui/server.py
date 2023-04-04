#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from asyncio import Future, run, get_running_loop
from os.path import dirname, realpath
from json import loads, dumps
from websockets import serve
from sys import path

GUI_DIR = realpath(dirname(__file__))
SRC_DIR = realpath(GUI_DIR + '/..')
DECOMPILATION_DIR = realpath(SRC_DIR + '/decompilation')
PARSERS_DIR = realpath(SRC_DIR + '/parsers')

path.insert(0, DECOMPILATION_DIR)
path.insert(0, GUI_DIR)

from defs import HermesDecompiler, DecompiledFunctionBody
from pass1_set_metadata import pass1_set_metadata
from pass1b_make_basic_blocks import pass1b_make_basic_blocks
from pass1c_visit_code_paths import pass1c_visit_code_paths

path.insert(0, PARSERS_DIR)

from hbc_bytecode_parser import parse_hbc_bytecode
from project_meta import ProjectSubdirManager
from hbc_file_parser import HBCReader

class ServerConnection:

    reader : HBCReader
    project : ProjectSubdirManager

    def create_file(self, file_name : str):
        self.project = ProjectSubdirManager.new_with_name(file_name)
    
    def write_to_file(self, bytes_slice : bytes):
        self.project.file_buffer.write(bytes_slice)
    
    def parse_file(self):
        self.reader = HBCReader()

        self.project.file_buffer.flush()
        self.project.file_buffer.seek(0)
        self.reader.read_whole_file(self.project.file_buffer)


async def echo(socket):
    loop = get_running_loop()
    connection = ServerConnection()

    async for msg in socket:
        
        if type(msg) == bytes:

            connection.write_to_file(msg)
        
        else:
            
            msg = loads(msg)

            print('DEBUG: Received: ', msg)

            msg_type = msg['type']

            # Please see the "../../../docs/GUI server websocket protocol.md"
            # file for documentation about the following messages.

            if msg_type == 'begin_transfer':
            
                connection.create_file(msg['file_name'])

            elif msg_type == 'end_transfer':

                await loop.run_in_executor(None, connection.parse_file)
                
                await socket.send(dumps({
                    'type': 'file_opened',
                    'functions_list': [
                        {
                            'name': connection.reader.strings[function.functionName] or 'fun_%08x' % function.offset,
                            'offset': '%08x' % function.offset,
                            'size': function.bytecodeSizeInBytes
                        }
                        for function in connection.reader.function_headers
                        # WIP ..
                    ]
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
                pass1c_visit_code_paths(state, dehydrated)

                # - Return the resulting pre-rendered/displayed graph as
                #   serialized JSON.

                draw_stuff(instructions, dehydrated)

                # WIP ..

            # elif msg_type == 'XX SEE. MD DOC':
                # WIP TODO ..

            # await websocket.send(message)

async def async_main():
    # TODO: Use a process (or thread but think of GIL) pool?
    # TODO: Implement the client/server communication defined within the
    # "docs/GUI server websocket protocol.md" file, as well as the GUI

    async with serve(echo, 'localhost', 49594):
        await Future()  # run forever

def main():
    run(async_main())

if __name__ == '__main__':
    main()