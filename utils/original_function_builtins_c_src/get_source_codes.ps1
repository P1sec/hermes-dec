# This script fetches various bits of Hermes source code to the current directory, for exploratory use.
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot


# Source the shared git tags and mapping
. "$PSScriptRoot\..\git_tags.ps1"

foreach ($git_tag in $GIT_TAGS) {
    $hbc_version = $TAG_TO_VERSION[$git_tag]
    Write-Host "Downloading files for $git_tag..."
    if (-not $hbc_version) {
        if ([string]::Compare($git_tag, 'v0.3.0') -le 0) {
            $url = "https://raw.githubusercontent.com/facebook/hermes/$git_tag/include/hermes/Inst/Builtins.def"
        } else {
            $url = "https://raw.githubusercontent.com/facebook/hermes/$git_tag/include/hermes/FrontEndDefs/Builtins.def"
        }
        $out = "Builtins-$git_tag.def"
        Invoke-WebRequest -Uri $url -OutFile $out -UseBasicParsing
    } else {
        $url1 = "https://raw.githubusercontent.com/facebook/hermes/$git_tag/include/hermes/FrontEndDefs/Builtins.def"
        $url2 = "https://raw.githubusercontent.com/facebook/hermes/$git_tag/include/hermes/Inst/Builtins.def"
        $out = "Builtins-$hbc_version.def"
        try {
            Invoke-WebRequest -Uri $url1 -OutFile $out -UseBasicParsing
        } catch {
            Invoke-WebRequest -Uri $url2 -OutFile $out -UseBasicParsing
        }
    }
}
