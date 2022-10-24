#!/bin/bash

# This script fetches various bits of Hermes source code
# to the current directory, for exploratory use.

# Exit on non-success
set -e

# How to list Hermes Git source tags:
# git -C ~/hermes fetch; git -C ~/hermes tag -l 'v*' | grep -v rc | sort -V | tr '\n' ' '; echo
# ("sort -V" means versioning-like sort)

GIT_TAGS='v0.0.1 v0.0.2 v0.0.3 v0.1.0 v0.1.1 v0.2.1 v0.3.0 v0.4.0 v0.4.1 v0.4.3 v0.4.4 v0.5.0 v0.5.1 v0.5.3 v0.6.0 v0.7.0 v0.7.1 v0.7.2 v0.8.0 v0.8.1 v0.9.0 v0.10.0 v0.11.0 v0.12.0'

verlte() {
    [  "$1" = "`echo -e "$1\n$2" | sort -V | head -n1`" ]
}

for git_tag in ${GIT_TAGS}; do
    echo "Downloading files for ${git_tag}..."
    if verlte "${git_tag}" "v0.8.0"; then
        wget -q "https://raw.githubusercontent.com/facebook/hermes/${git_tag}/include/hermes/BCGen/HBC/BytecodeFileFormat.h" -O "BytecodeVersion-${git_tag}.h"
    else
        wget -q "https://raw.githubusercontent.com/facebook/hermes/${git_tag}/include/hermes/BCGen/HBC/BytecodeVersion.h" -O "BytecodeVersion-${git_tag}.h"
    fi
    wget -q "https://raw.githubusercontent.com/facebook/hermes/${git_tag}/include/hermes/BCGen/HBC/BytecodeList.def" -O "BytecodeList-${git_tag}.def"
done
