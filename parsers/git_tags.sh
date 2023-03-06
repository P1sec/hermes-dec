#!/bin/bash

# This file is to be included by the code download scripts
# present in the current subdirectories.

# It contains Git tag identifiers and commit hashes for the
# single Hermes bytecode versions which are supported by
# the current tool. 

GIT_TAGS=(
    'v0.0.1' # Bytecode version 51
    # 'v0.0.2' # Bytecode version 51
    'v0.0.3' # Bytecode version 58
    'v0.1.0' # Bytecode version 59
    # 'v0.1.1' # Bytecode version 60 - No codegen change    
    'v0.2.1' # Bytecode version 62
    'v0.3.0' # Bytecode version 71
    'v0.4.0' # Bytecode version 74 - Bumped Jan 6, 2020 (there was a reverted version 75)
    # 'v0.4.1' # Bytecode version 74
    # 'v0.4.3' # Bytecode version 74
    # 'v0.4.4' # Bytecode version 74
    # 'v0.5.0' # Bytecode version 74
    # 'v0.5.1' # Bytecode version 74
    # 'v0.5.3' # Bytecode version 74
    # 'v0.6.0' # Bytecode version 74
    # '6871396' # Bytecode version 75 - Aug 3, 2020 - No gencode change
    'v0.7.0' # Bytecode version 76 - Bumped Aug 19, 2020
    # 'v0.7.1' # Bytecode version 76 - Bumped Aug 19, 2020
    # 'v0.7.2' # Bytecode version 76 - Bumped Aug 19, 2020, stable release Dec 9, 2020
    # '701b9dd' # Bytecode version 77 - Oct 7, 2020 - No gencode change
    # 'c57fde2' # Bytecode version 78 - Oct 8, 2020 - No gencode change
    # '05b2972' # Bytecode version 79 - Dec 29, 2020 - No gencode change
    'e70045d' # Bytecode version 80 - Jan 13, 2021
    '40aa0f7' # Bytecode version 81 - Jan 14, 2021
    '65de349' # Bytecode version 82 - Jan 26, 2021
    'v0.8.0' # Bytecode version 83 - Bumped Mar 16, 2021, stable release Apr 29, 2021
    # 'v0.8.1' # Bytecode version 84 - Bumped Jul 10, 2021, stable release Jul 12, 2021
    # WebAssembly instrinsincs are added in bytecode versions 85 and 86, but the
    # bytecode version number is then unbumped as these have been disabled by default.
    'v0.9.0' # Bytecode version 84 - Unbumped from 86 Jul 27, 2021, stable release Sep 2, 2021
    # 'v0.10.0' # Bytecode version 84 - Unbumped from 86 Jul 27, 2021, stable release Nov 14, 2021
    'v0.11.0' # Bytecode version 85 - Bumped Mar 22, 2022, stable release Jan 27, 2022
    'b823515' # Bytecode version 86 - Jun 28, 2022
    '41752c6' # Bytecode version 87 - Jul 9, 2022
    # '2a55135' # Bytecode version 88 - Jul 9, 2022 - No gencode change
    'v0.12.0' # Bytecode version 89 - Bumped Jul 14, 2022, stable release Aug 24, 2022
    '0763eee' # Bytecode version 90 - Oct 7, 2022
    # '4985960' # Bytecode version 91 - Dec 18, 2022 - No gencode change
    # Bytecode version 92 contains a change that was reverted from the main source
    # tree after three days (Feb 14-17, 2023).
    # Bytecode version 93 is similar to bytecode version 91.
)

declare -A TAG_TO_VERSION=(
    [6871396]='hbc75'
    [701b9dd]='hbc77'
    [c57fde2]='hbc78'
    [05b2972]='hbc79'
    [e70045d]='hbc80'
    [40aa0f7]='hbc81'
    [65de349]='hbc82'
    [b74eb2d]='hbc85'
    [b823515]='hbc86'
    [41752c6]='hbc87'
    [2a55135]='hbc88'
    [0763eee]='hbc90'
    [4985960]='hbc91'
)
