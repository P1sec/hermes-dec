#!/bin/bash
set -ex

cd "$(dirname "$0")"

../parsers/hbc_file_parser.py assets/index.android.bundle > sample_real.hermes_dec_header
../disassembly/hbc_disassembler.py assets/index.android.bundle sample_real.hermes_dec_hasm
../decompilation/hbc_decompiler.py assets/index.android.bundle sample_real.hermes_dec_hdec
