# bump_patch.ps1 - Increment the patch (3rd) version number
#
# Usage:
#   .\bump_patch.ps1
#
# Updates:
#   pyproject.toml          version = "X.Y.Z"
#   __version__.py          PROJECT_FALLBACK_VERSION = "X.Y.Z"
#   AppxManifest.xml        Version="X.Y.Z.0"

$ErrorActionPreference = 'Stop'
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

# Read current version from pyproject.toml
$toml = Join-Path $root 'pyproject.toml'
$tomlContent = Get-Content $toml -Raw -Encoding UTF8

if ($tomlContent -notmatch 'version\s*=\s*"(\d+)\.(\d+)\.(\d+)"') {
    Write-Error "Cannot read version from pyproject.toml"
    exit 1
}
$major    = [int]$Matches[1]
$minor    = [int]$Matches[2]
$patch    = [int]$Matches[3]
$newPatch = $patch + 1

$oldVer  = ('{0}.{1}.{2}'   -f $major, $minor, $patch)
$newVer  = ('{0}.{1}.{2}'   -f $major, $minor, $newPatch)
$oldVerW = ('{0}.{1}.{2}.0' -f $major, $minor, $patch)
$newVerW = ('{0}.{1}.{2}.0' -f $major, $minor, $newPatch)

Write-Host ('Bump: ' + $oldVer + '  ->  ' + $newVer)

# pyproject.toml
$pat1    = 'version\s*=\s*"' + [regex]::Escape($oldVer) + '"'
$rep1    = 'version = "' + $newVer + '"'
$tomlNew = $tomlContent -replace $pat1, $rep1
[System.IO.File]::WriteAllText($toml, $tomlNew, $utf8NoBom)
Write-Host '  Updated: pyproject.toml'

# __version__.py
$vpy     = Join-Path $root '__version__.py'
$vpyCont = Get-Content $vpy -Raw -Encoding UTF8
$pat2    = 'PROJECT_FALLBACK_VERSION\s*=\s*"' + [regex]::Escape($oldVer) + '"'
$rep2    = 'PROJECT_FALLBACK_VERSION = "' + $newVer + '"'
$vpyNew  = $vpyCont -replace $pat2, $rep2
[System.IO.File]::WriteAllText($vpy, $vpyNew, $utf8NoBom)
Write-Host '  Updated: __version__.py'

# AppxManifest.xml
$xml     = Join-Path $root 'AppxManifest.xml'
$xmlCont = Get-Content $xml -Raw -Encoding UTF8
$pat3    = 'Version="' + [regex]::Escape($oldVerW) + '"'
$rep3    = 'Version="' + $newVerW + '"'
$xmlNew  = $xmlCont -replace $pat3, $rep3
[System.IO.File]::WriteAllText($xml, $xmlNew, $utf8NoBom)
Write-Host '  Updated: AppxManifest.xml'

Write-Host ('Done. New version: ' + $newVer)