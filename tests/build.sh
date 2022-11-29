#!/bin/bash
set -ex

cd "$(dirname "$0")"

~/hermes/build/bin/hermesc -emit-binary -out=sample.hbc sample.js

echo disassemble | ~/hermes/build/bin/hbcdump  -raw-disassemble ../tests/sample.hbc
