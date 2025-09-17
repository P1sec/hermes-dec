# This file provides Git tag identifiers and commit hashes for Hermes bytecode versions, for use in PowerShell scripts.

# List of supported Git tags
$GIT_TAGS = @(
    'v0.0.1',
    'v0.0.3',
    'v0.1.0',
    'ee7a2db',
    'v0.2.1',
    '883eb4d',
    '5a402ac',
    '51969f2',
    'd1637f2',
    'ecded4d',
    'v0.7.0',
    'e70045d',
    '40aa0f7',
    '65de349',
    'v0.8.0',
    'v0.9.0',
    'v0.11.0',
    'b823515',
    '41752c6',
    'v0.12.0',
    '0763eee',
    'b544ff4',
    'f6b56d3'
)

# Mapping from Git tag/commit to Hermes bytecode version
$TAG_TO_VERSION = @{
    'ee7a2db' = 'hbc61'
    '8eb5923' = 'hbc63'
    '2d326de' = 'hbc64'
    '28436fb' = 'hbc65'
    '892bf2c' = 'hbc66'
    'f9e263d' = 'hbc67'
    '883eb4d' = 'hbc68'
    '5a402ac' = 'hbc69'
    '51969f2' = 'hbc70'
    'd1637f2' = 'hbc72'
    'ecded4d' = 'hbc73'
    '6871396' = 'hbc75'
    '701b9dd' = 'hbc77'
    'c57fde2' = 'hbc78'
    '05b2972' = 'hbc79'
    'e70045d' = 'hbc80'
    '40aa0f7' = 'hbc81'
    '65de349' = 'hbc82'
    'b74eb2d' = 'hbc85'
    'b823515' = 'hbc86'
    '41752c6' = 'hbc87'
    '2a55135' = 'hbc88'
    '0763eee' = 'hbc90'
    '4985960' = 'hbc91'
    'b544ff4' = 'hbc92'
    '1c71748' = 'hbc94'
    'f6b56d3' = 'hbc95'
}
