#!/usr/bin/env python3
# -*- encoding: Utf-8 -*-
from os.path import dirname, realpath
from os import execlp, chdir
import sys

SCRIPT_DIR = dirname(realpath(__file__))
sys.path.append(SCRIPT_DIR)


def main():
    chdir(SCRIPT_DIR)

    execlp('bash', 'bash', './regen_hbc_regex_parser.sh', *sys.argv[1:])


if __name__ == '__main__':
    main()
