#!/bin/bash

# This script fetches various bits of Hermes source code
# to the current directory, for exploratory use.

# Exit on non-success
set -e

# How to list Hermes Git source tags:
# git -C ~/hermes fetch; git -C ~/hermes tag -l 'v*' | grep -v rc | sort -V | tr '\n' ' '; echo
# ("sort -V" means versioning-like sort)

cd "$(dirname "$0")"
source ../git_tags.sh

verlte() {
    [  "$1" = "$(echo -e "$1\n$2" | sort -V | head -n1)" ]
}

for git_tag in ${GIT_TAGS[@]}; do
    hbc_version=${TAG_TO_VERSION[${git_tag}]}

    echo "Downloading files for ${git_tag}..."
    if [ -z ${hbc_version} ]; then
        if verlte "${git_tag}" "v0.8.0"; then
            wget "https://raw.githubusercontent.com/facebook/hermes/${git_tag}/include/hermes/BCGen/HBC/BytecodeFileFormat.h" -O "BytecodeVersion-${git_tag}.h"
        else
            wget "https://raw.githubusercontent.com/facebook/hermes/${git_tag}/include/hermes/BCGen/HBC/BytecodeVersion.h" -O "BytecodeVersion-${git_tag}.h"
        fi
        wget "https://raw.githubusercontent.com/facebook/hermes/${git_tag}/include/hermes/BCGen/HBC/BytecodeList.def" -O "BytecodeList-${git_tag}.def"
    else
        wget "https://raw.githubusercontent.com/facebook/hermes/${git_tag}/include/hermes/BCGen/HBC/BytecodeVersion.h" -O "BytecodeVersion-${hbc_version}.h"
        wget "https://raw.githubusercontent.com/facebook/hermes/${git_tag}/include/hermes/BCGen/HBC/BytecodeList.def" -O "BytecodeList-${hbc_version}.def"
    fi
done
