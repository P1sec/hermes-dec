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
    [  "$1" = "`echo -e "$1\n$2" | sort -V | head -n1`" ]
}

for git_tag in ${GIT_TAGS[@]}; do
    hbc_version=${TAG_TO_VERSION[${git_tag}]}

    echo "Downloading files for ${git_tag}..."
    if [ -z ${hbc_version} ]; then
        if verlte "${git_tag}" "v0.3.0"; then
            wget "https://raw.githubusercontent.com/facebook/hermes/${git_tag}/include/hermes/Inst/Builtins.def" -O "Builtins-${git_tag}.def"
        else
            wget "https://raw.githubusercontent.com/facebook/hermes/${git_tag}/include/hermes/FrontEndDefs/Builtins.def" -O "Builtins-${git_tag}.def"
        fi
    else
        wget "https://raw.githubusercontent.com/facebook/hermes/${git_tag}/include/hermes/FrontEndDefs/Builtins.def" -O "Builtins-${hbc_version}.def"
    fi
done
