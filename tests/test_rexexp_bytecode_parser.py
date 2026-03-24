from io import BytesIO

from hermes_dec.parsers.regexp_bytecode_parser import decompile_regex, parse_regex, escape


def test_escaping_character_sequences():
    assert escape('://') == r':\/\/'

def test_regexp_with_quoted_backslash():
    d = decompile_regex(
        parse_regex(
            96, BytesIO(b'\x00\x00\x02\x00\x00\x06\x01\n\x04http\x1c\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x1b\x00\x00\x00\x07s\n\x03://\x1c\x01\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\x003\x00\x00\x00\x05\x07/\x00')
        )
    )
    assert d == r'/^https?:\/\/.*?\//'


