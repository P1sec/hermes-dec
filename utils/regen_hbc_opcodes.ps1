# Exit on error
$ErrorActionPreference = "Stop"

# Change to the script's directory
Set-Location -Path $PSScriptRoot

# Remove .def and .h files
Remove-Item -Force -ErrorAction SilentlyContinue .\original_function_builtins_c_src\*.def
Remove-Item -Force -ErrorAction SilentlyContinue .\original_hermes_bytecode_c_src\*.def
Remove-Item -Force -ErrorAction SilentlyContinue .\original_hermes_bytecode_c_src\*.h

# Run the source code fetching scripts
& .\original_hermes_bytecode_c_src\get_source_codes.ps1
& .\original_function_builtins_c_src\get_source_codes.ps1
# & .\original_regex_bytecode_c_src\get_source_codes.ps1

# Run the Python parser
& .\hermes_bytecode_structs_parser.py
