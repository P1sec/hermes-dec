#!/bin/bash

# Exit on non-success, print commands
set -ex

cd "$(dirname "$0")"

rm -f original_regex_bytecode_c_src/*.h

./original_regex_bytecode_c_src/get_source_codes.sh

./regex_bytecode_structs_parser.py

cd ..
ruff format

