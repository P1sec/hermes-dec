#!/bin/bash

# This file is to be included by the code download scripts
# present in the current subdirectories.

# It contains Git tag identifiers and commit hashes for the
# single Hermes bytecode versions which are supported by
# the current tool. 

GIT_TAGS=(
    'v0.0.1'
    'v0.0.2'
    'v0.0.3'
    'v0.1.0'
    'v0.1.1'
    'v0.2.1'
    'v0.3.0'
    'v0.4.0'
    'v0.4.1'
    'v0.4.3'
    'v0.4.4'
    'v0.5.0'
    'v0.5.1'
    'v0.5.3'
    'v0.6.0'
    'v0.7.0'
    'v0.7.1'
    'v0.7.2'
    'v0.8.0'
    'v0.8.1'
    'v0.9.0'
    'v0.10.0'
    'v0.11.0' # Bytecode version 84 - Bumped Jul 10, 2021, stable release Nov 14, 2021
    'b74eb2d' # Bytecode version 85 - Mar 22, 2022
    'b823515' # Bytecode version 86 - Jun 28, 2022
    '41752c6' # Bytecode version 87 - Jul 9, 2022
    '2a55135' # Bytecode version 88 - Jul 9, 2022
    'v0.12.0' # Bytecode version 89 - Bumped Jul 14, 2022, stable release Aug 24, 2022
)

declare -A TAG_TO_VERSION=(
    [b74eb2d]='hbc84'
    [b823515]='hbc85'
    [41752c6]='hbc86'
    [2a55135]='hbc87'
)
