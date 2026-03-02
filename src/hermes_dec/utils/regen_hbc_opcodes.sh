#!/bin/bash

# Exit on non-success, print commands
set -ex

cd "$(dirname "$0")"

rm -f original_function_builtins_c_src/*.def
rm -f original_hermes_bytecode_c_src/*.def
rm -f original_hermes_bytecode_c_src/*.h

./original_hermes_bytecode_c_src/get_source_codes.sh
./original_function_builtins_c_src/get_source_codes.sh
# ./original_regex_bytecode_c_src/get_source_codes.sh

./hermes_bytecode_structs_parser.py

