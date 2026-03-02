# This script fetches various bits of Hermes source code to the current directory, for exploratory use.
$ErrorActionPreference = "Stop"
Push-Location -Path $PSScriptRoot


# Source the shared git tags and mapping
. "$PSScriptRoot\..\git_tags.ps1"

function verlte($a, $b) {
    $v = @($a, $b) | Sort-Object {[version]($_ -replace '[^0-9.]', '')}
    $minimal = ($v[0] -replace '[^0-9.]', '')
    $first = ($a -replace '[^0-9.]', '')
    $result = $first -eq $minimal
    return $result
}

foreach ($git_tag in $GIT_TAGS) {
    $hbc_version = $TAG_TO_VERSION[$git_tag]
    Write-Host "Downloading files for $git_tag..."
    if (-not $hbc_version) {
        if (verlte $git_tag 'v0.8.0') {
            $url = "https://raw.githubusercontent.com/facebook/hermes/$git_tag/include/hermes/BCGen/HBC/BytecodeFileFormat.h"
            $out = "BytecodeVersion-$git_tag.h"
            echo "Trying $url ..."
            Invoke-WebRequest -Uri $url -OutFile $out -UseBasicParsing
        } else {
            $url = "https://raw.githubusercontent.com/facebook/hermes/$git_tag/include/hermes/BCGen/HBC/BytecodeVersion.h"
            $out = "BytecodeVersion-$git_tag.h"
            echo "Trying $url ..."
            Invoke-WebRequest -Uri $url -OutFile $out -UseBasicParsing
        }
        $url2 = "https://raw.githubusercontent.com/facebook/hermes/$git_tag/include/hermes/BCGen/HBC/BytecodeList.def"
        $out2 = "BytecodeList-$git_tag.def"
        echo "Trying $url2 ..."
        Invoke-WebRequest -Uri $url2 -OutFile $out2 -UseBasicParsing
    } else {
        $url1 = "https://raw.githubusercontent.com/facebook/hermes/$git_tag/include/hermes/BCGen/HBC/BytecodeVersion.h"
        $url2 = "https://raw.githubusercontent.com/facebook/hermes/$git_tag/include/hermes/BCGen/HBC/BytecodeFileFormat.h"
        $out = "BytecodeVersion-$hbc_version.h"
        try {
            Invoke-WebRequest -Uri $url1 -OutFile $out -UseBasicParsing
        } catch {
            Invoke-WebRequest -Uri $url2 -OutFile $out -UseBasicParsing
        }
        $url3 = "https://raw.githubusercontent.com/facebook/hermes/$git_tag/include/hermes/BCGen/HBC/BytecodeList.def"
        $out3 = "BytecodeList-$hbc_version.def"
        Invoke-WebRequest -Uri $url3 -OutFile $out3 -UseBasicParsing
    }
}

Pop-Location