# build_nuitka.ps1 - Build a Python application into a standalone executable with Nuitka
#
# This script:
# 1) Ensures LLVM/clang is installed (installs via Chocolatey if missing)
# 2) Adds LLVM to PATH
# 3) Syncs dependencies with uv
# 4) Builds the executable using Nuitka with clang
#
# Usage examples:
#   ./build_nuitka.ps1
#   ./build_nuitka.ps1 -EntryScript 'main_window.py' -OutputDir 'dist' -OutputFileName 'PandocGUI'
#   ./build_nuitka.ps1 -SkipUvSync

[CmdletBinding()]
param(
    [string]$EntryScript = 'main_window.py',
    [string]$OutputDir = 'dist',
    [string]$OutputFileName = 'PandocGUI',
    [switch]$SkipUvSync
)

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

function Remove-PathIfExists {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Recurse -Force
        Write-Host ('  Removed: ' + $Path)
    }
}

Push-Location $root
try {
    $entryBaseName = [System.IO.Path]::GetFileNameWithoutExtension($EntryScript)
    if (-not $entryBaseName) {
        throw ('Invalid EntryScript: ' + $EntryScript)
    }

    Write-Host 'Prep: Clean previous Nuitka artifacts'
    $inputDistPath = Join-Path $OutputDir ($entryBaseName + '.dist')
    $inputBuildPath = Join-Path $OutputDir ($entryBaseName + '.build')
    $exeFileName = if ($OutputFileName.ToLowerInvariant().EndsWith('.exe')) { $OutputFileName } else { $OutputFileName + '.exe' }
    $inputExePath = Join-Path $OutputDir $exeFileName

    Remove-PathIfExists -Path (Join-Path $root $inputDistPath)
    Remove-PathIfExists -Path (Join-Path $root $inputBuildPath)
    Remove-PathIfExists -Path (Join-Path $root $inputExePath)

    Write-Host 'Step 1/3: Sync dependencies'
    if (-not $SkipUvSync) {
        & uv sync --group build
        if ($LASTEXITCODE -ne 0) {
            throw ('uv sync failed with exit code ' + $LASTEXITCODE)
        }
    } else {
        Write-Host 'Skipping uv sync'
    }

    Write-Host 'Step 2/3: Ensure LLVM is installed'
    
    # Add LLVM to PATH if not already present (before checking for clang-cl)
    $llvmBinPath = 'C:\Program Files\LLVM\bin'
    if ($env:PATH -notlike "*$llvmBinPath*") {
        $env:PATH = "$llvmBinPath;$($env:PATH)"
    }
    
    # Check if clang-cl is installed
    $clangClPath = where.exe clang-cl 2>$null
    if (-not $clangClPath) {
        Write-Host 'clang-cl not found. Installing LLVM via Chocolatey...'
        
        # Check if running as admin
        $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
        $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
        $isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        
        if (-not $isAdmin) {
            throw 'Administrator privileges required to install LLVM. Please run this script as Administrator.'
        }
        
        & choco install llvm -y
        if ($LASTEXITCODE -ne 0) {
            throw ('Chocolatey LLVM installation failed with exit code ' + $LASTEXITCODE)
        }
        
        Write-Host 'LLVM installed successfully.'
        Write-Host "Added $llvmBinPath to PATH"
    }
    
    Write-Host 'Step 3/3: Build with Nuitka'
    $env:CC = 'clang-cl'
    $env:CXX = 'clang-cl'

    $nuitkaOptions = @(
        '--clang',
        '--msvc=latest',
        '--onefile',
        '--windows-console-mode=disable',
        '--enable-plugin=tk-inter',
        "--output-dir=$OutputDir",
        "--output-filename=$OutputFileName",
        '--include-data-dir=filters=filters',
        '--include-data-dir=locales=locales',
        '--include-data-dir=stylesheets=stylesheets',
        '--include-data-dir=help=help',
        '--include-data-dir=profiles=profiles',
        '--include-data-dir=mermaid=mermaid',
        '--include-data-dir=LICENSES=LICENSES',
        $EntryScript
    )

    $nuitkaArgs = @('-m', 'nuitka') + $nuitkaOptions
    & uv run python @nuitkaArgs
    if ($LASTEXITCODE -ne 0) {
        throw ('Nuitka build failed with exit code ' + $LASTEXITCODE)
    }

    Write-Host ''
    Write-Host 'Build completed successfully.'
    Write-Host ('EXE: ' + (Join-Path $root $inputExePath))
}
finally {
    Pop-Location
}
