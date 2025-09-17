# This script fetches various bits of Hermes source code to the current directory, for exploratory use.
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

# Source the shared git tags and mapping
. "$PSScriptRoot\..\git_tags.ps1"

foreach ($git_tag in $GIT_TAGS) {
    $hbc_version = $TAG_TO_VERSION[$git_tag]
    if (-not $hbc_version) { $hbc_version = $git_tag }
    Write-Host "Downloading files for $git_tag..."
    $url = "https://raw.githubusercontent.com/facebook/hermes/$git_tag/include/hermes/Regex/RegexBytecode.h"
    $out = "RegexBytecode-$hbc_version.h"
    Invoke-WebRequest -Uri $url -OutFile $out -UseBasicParsing
}
