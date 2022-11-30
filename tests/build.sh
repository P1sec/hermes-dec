#!/bin/bash
set -ex

cd "$(dirname "$0")"

~/hermes/build/bin/hermesc -emit-binary -out=sample.hbc sample.js

echo disassemble | ~/hermes/build/bin/hbcdump  -raw-disassemble sample.hbc > sample.hermes_raw_hasm
echo disassemble | ~/hermes/build/bin/hbcdump  -pretty-disassemble sample.hbc > sample.hermes_pretty_hasm
echo disassemble | ~/hermes/build/bin/hbcdump  -objdump-disassemble sample.hbc > sample.hermes_objdump_hasm

../parsers/hbc_file_parser.py sample.hbc > sample.hermes_dec_header
../disassembly/hbc_disassembler.py sample.hbc sample.hermes_dec_hasm
../decompilation/hbc_decompiler.py sample.hbc sample.hermes_dec_hdec

# Currently not functional: PYTHONPATH=/home/marin/atypikoo_apk/hbctool/ python3 ~/atypikoo_apk/hbctool/hbctool/__init__.py disasm sample.hbc sample.hbctool_py_hasm
