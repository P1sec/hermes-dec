#!/bin/bash
set -x
# set -e: exit on error

cd "$(dirname "$0")"

DIR="version-99-202602"
~/hermes/build/bin/hermesc -emit-binary -out=${DIR}/sample.hbc ${DIR}/sample.js

echo disassemble | ~/hermes/build/bin/hbcdump  -raw-disassemble ${DIR}/sample.hbc > ${DIR}/sample.hermes_raw_hasm
echo disassemble | ~/hermes/build/bin/hbcdump  -pretty-disassemble ${DIR}/sample.hbc > ${DIR}/sample.hermes_pretty_hasm
echo disassemble | ~/hermes/build/bin/hbcdump  -objdump-disassemble ${DIR}/sample.hbc > ${DIR}/sample.hermes_objdump_hasm

for DIR in version-84 version-94 version-99-202602; do # ~/hermes-dec-samples/version-98-issue19
    ../hbc-file-parser ${DIR}/sample.hbc > ${DIR}/sample.hermes_dec_header
    ../hbc-disassembler ${DIR}/sample.hbc ${DIR}/sample.hermes_dec_hasm
    ../hbc-decompiler ${DIR}/sample.hbc ${DIR}/sample.hermes_dec_hdec
done

# Currently not functional: PYTHONPATH=/home/marin/atypikoo_apk/hbctool/ python3 ~/atypikoo_apk/hbctool/hbctool/__init__.py disasm sample.hbc sample.hbctool_py_hasm
