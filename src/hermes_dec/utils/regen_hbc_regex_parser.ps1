# Exit on error
$ErrorActionPreference = "Stop"

# Change to the script's directory
Set-Location -Path $PSScriptRoot

# Remove .def and .h files
Remove-Item -Force -ErrorAction SilentlyContinue .\original_regex_bytecode_c_src\*.h

# Run the source code fetching scripts
& .\original_regex_bytecode_c_src\get_source_codes.ps1

# Run the Python parser
python .\regex_bytecode_structs_parser.py

cd ..
ruff format

Pop-Location
