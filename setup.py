#!/usr/bin/python3
#-*- encoding: Utf-8 -*-

from setuptools import setup

setup(name = 'hermes-dec',
    version = '0.0.1',
    description = 'A tool for reverse engineering React Native bytecode files, including disassembly and decompilation facilities',
    author = 'P1 Security - Marin Moulinier',
    author_email = '',
    entry_points = {
        'console_scripts': [
            'hbc-decompiler = hermes_dec.decompilation.hbc_decompiler:main',
            'hbc-disassembler = hermes_dec.disassembly.hbc_disassembler:main',
            'hbc-file-parser = hermes_dec.parsers.hbc_file_parser:main'
        ]
    },
    url = 'https://github.com/P1sec/hermes-dec',
    install_requires = [],
    packages = [
        'hermes_dec.parsers',
        'hermes_dec.parsers.hbc_opcodes',
        'hermes_dec.decompilation',
        'hermes_dec.disassembly'
    ],
    package_dir = {
        'hermes_dec.parsers': 'src/parsers',
        'hermes_dec.disassembly': 'src/disassembly',
        'hermes_dec.decompilation': 'src/decompilation'
    }
)
