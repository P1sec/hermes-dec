#!/bin/bash

# This script fetches various bits of Hermes source code
# to the current directory, for exploratory use.

# Exit on non-success
set -e

# How to list Hermes Git source tags:
# git -C ~/hermes fetch; git -C ~/hermes tag -l 'v*' | grep -v rc | sort -V | tr '\n' ' '; echo
# ("sort -V" means versioning-like sort)

GIT_TAGS='v0.0.1 v0.0.2 v0.0.3 v0.1.0 v0.1.1 v0.2.1 v0.3.0 v0.4.0 v0.4.1 v0.4.3 v0.4.4 v0.5.0 v0.5.1 v0.5.3 v0.6.0 v0.7.0 v0.7.1 v0.7.2 v0.8.0 v0.8.1 v0.9.0 v0.10.0 v0.11.0 v0.12.0'

for git_tag in ${GIT_TAGS}; do
    echo "Downloading files for ${git_tag}..."
    wget -q "https://raw.githubusercontent.com/facebook/hermes/${git_tag}/include/hermes/Regex/RegexBytecode.h" -O "RegexBytecode-${git_tag}.h"
done
