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

for git_tag in ${GIT_TAGS[@]}; do
    hbc_version=${TAG_TO_VERSION[${git_tag}]}
    if [ -z ${hbc_version} ]; then
        hbc_version=${git_tag}
    fi

    echo "Downloading files for ${git_tag}..."
    wget "https://raw.githubusercontent.com/facebook/hermes/${git_tag}/include/hermes/Regex/RegexBytecode.h" -O "RegexBytecode-${hbc_version}.h"
done
