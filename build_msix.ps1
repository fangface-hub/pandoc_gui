# build_msix.ps1 - Create an MSIX package from Nuitka output
#
# Usage examples:
#   ./build_msix.ps1
#   ./build_msix.ps1 -PublisherCN "CN=YourName" -IdentityName "YourName.PandocGUI" -PublisherDisplayName "YourName"
#   ./build_msix.ps1 -OutputMsixPath ./dist/PandocGUI-1.3.4.msix
#
# Notes:
# - Requires makeappx.exe (Windows SDK)
# - Expects Nuitka output at dist/main_window.dist by default

[CmdletBinding()]
param(
    [string]$InputDistPath = 'dist/main_window.dist',
    [string]$InputExePath,
    [string]$ManifestPath = 'AppxManifest.xml',
    [string]$OutputMsixPath = 'dist/PandocGUI.msix',
    [string]$StageDir = 'dist/msix',

    [string]$PublisherCN = 'CN=YourName',
    [string]$IdentityName = "$env:USERNAME.PandocGUI",
    [string]$PublisherDisplayName = "$env:USERNAME",
    [string]$Version,

    [string]$Logo150Path = 'Square150x150Logo.png',
    [string]$Logo44Path = 'Square44x44Logo.png',
    [string]$AppFolderName = 'PandocGUI',
    [string[]]$ResourceFolders = @('filters',
        'help',
        'LICENSES',
        'locales',
        'mermaid',
        'profiles',
        'stylesheets'),

    [string]$MakeAppxPath
)

$ErrorActionPreference = 'Stop'

function Find-MakeAppx {
    $cmd = Get-Command makeappx.exe -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    $kitRoot = 'C:\Program Files (x86)\Windows Kits\10\bin'
    if (-not (Test-Path -LiteralPath $kitRoot)) {
        return $null
    }

    $versions = Get-ChildItem $kitRoot -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match '^\d+\.\d+\.\d+\.\d+$' } |
        Sort-Object Name -Descending

    foreach ($version in $versions) {
        $candidate = Join-Path $version.FullName 'x64\makeappx.exe'
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }

    return $null
}

function Ensure-ParentDirectory {
    param([Parameter(Mandatory = $true)][string]$Path)

    $parent = Split-Path -Parent $Path
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
}

function Resolve-ProjectVersion {
    param([string]$ProjectTomlPath)

    if (-not (Test-Path -LiteralPath $ProjectTomlPath)) {
        throw ('pyproject.toml not found: ' + $ProjectTomlPath)
    }

    $tomlContent = Get-Content -LiteralPath $ProjectTomlPath -Raw -Encoding UTF8
    if ($tomlContent -notmatch 'version\s*=\s*"([0-9]+(?:\.[0-9]+){2,3})"') {
        throw 'Cannot read version from pyproject.toml'
    }

    return $Matches[1]
}

$useOnefileLayout = $false
if ($InputExePath -and (Test-Path -LiteralPath $InputExePath)) {
    $useOnefileLayout = $true
} elseif (-not (Test-Path -LiteralPath $InputDistPath)) {
    throw ('Input dist directory not found: ' + $InputDistPath)
}
if (-not (Test-Path -LiteralPath $ManifestPath)) {
    throw ('Manifest not found: ' + $ManifestPath)
}
if (-not (Test-Path -LiteralPath $Logo150Path)) {
    throw ('Logo not found: ' + $Logo150Path)
}
if (-not (Test-Path -LiteralPath $Logo44Path)) {
    throw ('Logo not found: ' + $Logo44Path)
}

$projectVersion = if ($Version) { $Version } else { Resolve-ProjectVersion -ProjectTomlPath 'pyproject.toml' }
$parts = $projectVersion.Split('.')
if ($parts.Length -eq 3) {
    $msixVersion = "$projectVersion.0"
} elseif ($parts.Length -eq 4) {
    $msixVersion = $projectVersion
} else {
    throw ('Version must be in x.y.z or x.y.z.w format: ' + $projectVersion)
}

if (-not $MakeAppxPath) {
    $MakeAppxPath = Find-MakeAppx
}
if (-not $MakeAppxPath) {
    throw 'makeappx.exe not found. Install Windows SDK or specify -MakeAppxPath.'
}

$cwdPath = (Get-Location).Path
$absStageDir = (Join-Path $cwdPath $StageDir)
$absInputDist = $null
if (-not $useOnefileLayout) {
    $absInputDist = (Resolve-Path -LiteralPath $InputDistPath).Path
}
$absManifest = (Resolve-Path -LiteralPath $ManifestPath).Path
$absLogo150 = (Resolve-Path -LiteralPath $Logo150Path).Path
$absLogo44 = (Resolve-Path -LiteralPath $Logo44Path).Path
$absOutputMsix = (Join-Path $cwdPath $OutputMsixPath)

Ensure-ParentDirectory -Path $absOutputMsix

if (Test-Path -LiteralPath $absStageDir) {
    Remove-Item -LiteralPath $absStageDir -Recurse -Force
}
New-Item -ItemType Directory -Path $absStageDir -Force | Out-Null

# MSIX root layout
$appDir = Join-Path $absStageDir $AppFolderName
if ($useOnefileLayout) {
    New-Item -ItemType Directory -Path $appDir -Force | Out-Null
    $absInputExe = (Resolve-Path -LiteralPath $InputExePath).Path
    Copy-Item -LiteralPath $absInputExe -Destination (Join-Path $appDir 'PandocGUI.exe') -Force

    foreach ($folder in $ResourceFolders) {
        $folderPath = Join-Path $cwdPath $folder
        if (Test-Path -LiteralPath $folderPath) {
            Copy-Item -LiteralPath $folderPath -Destination (Join-Path $appDir $folder) -Recurse -Force
        }
    }
} else {
    Copy-Item -LiteralPath $absInputDist -Destination $appDir -Recurse -Force
}
Copy-Item -LiteralPath $absManifest -Destination (Join-Path $absStageDir 'AppxManifest.xml') -Force
Copy-Item -LiteralPath $absLogo150 -Destination (Join-Path $absStageDir 'Square150x150Logo.png') -Force
Copy-Item -LiteralPath $absLogo44 -Destination (Join-Path $absStageDir 'Square44x44Logo.png') -Force

# Configure identity in staged manifest
$stagedManifestPath = Join-Path $absStageDir 'AppxManifest.xml'
[xml]$manifestXml = Get-Content -LiteralPath $stagedManifestPath
$manifestXml.Package.Identity.Publisher = $PublisherCN
$manifestXml.Package.Identity.Name = $IdentityName
$manifestXml.Package.Identity.Version = $msixVersion
$manifestXml.Package.Properties.PublisherDisplayName = $PublisherDisplayName

$currentExecutable = [string]$manifestXml.Package.Applications.Application.Executable
if ($currentExecutable) {
    $exeName = Split-Path -Leaf $currentExecutable
    if (-not $exeName) {
        $exeName = 'PandocGUI.exe'
    }
    $manifestXml.Package.Applications.Application.Executable = ($AppFolderName + '\' + $exeName)
}

$manifestXml.Save($stagedManifestPath)

Write-Host ('Using makeappx: ' + $MakeAppxPath)
Write-Host ('Version      : ' + $msixVersion)
Write-Host ('Publisher    : ' + $PublisherCN)
Write-Host ('IdentityName : ' + $IdentityName)
Write-Host ('Output       : ' + $absOutputMsix)

& $MakeAppxPath pack /d $absStageDir /p $absOutputMsix /o
if ($LASTEXITCODE -ne 0) {
    throw ('makeappx pack failed with exit code ' + $LASTEXITCODE)
}

Write-Host 'Done. MSIX package created successfully.'