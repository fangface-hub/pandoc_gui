# build_nuitka_msix_signed.ps1 - Orchestrate building, packaging, and signing MSIX
#
# Default flow:
# 1) Build dist/PandocGUI.exe with Nuitka (using build_nuitka.ps1)
# 2) Create MSIX package using build_msix.ps1
# 3) Sign and verify MSIX using sign_msix.ps1
#
# Usage examples:
#   ./build_nuitka_msix_signed.ps1
#   ./build_nuitka_msix_signed.ps1 -PublisherCN "CN=YourName" -IdentityName "YourName.PandocGUI" -PublisherDisplayName "YourName"
#   ./build_nuitka_msix_signed.ps1 -PfxPath ./certificate.pfx -PfxPassword (Read-Host "PFX password" -AsSecureString)
#   ./build_nuitka_msix_signed.ps1 -SkipNuitkaBuild

[CmdletBinding()]
param(
    [string]$EntryScript = 'main_window.py',
    [string]$OutputDir = 'dist',
    [string]$OutputFileName = 'PandocGUI',

    [string]$OutputMsixPath = 'dist/PandocGUI.msix',
    [string]$StageDir = 'dist/msix',
    [string]$ManifestPath = 'AppxManifest.xml',

    [string]$PublisherCN = 'CN=YourName',
    [string]$IdentityName = "$env:USERNAME.PandocGUI",
    [string]$PublisherDisplayName = "$env:USERNAME",
    [string]$Version,

    [string]$PfxPath,
    [securestring]$PfxPassword,
    [string]$Thumbprint,
    [string]$ExportCerPath = 'dist/PandocGUI.cer',
    [string]$TimestampServer = 'http://timestamp.digicert.com',
    [string]$SignToolPath,

    [switch]$SkipNuitkaBuild,
    [switch]$SkipSigning,
    [switch]$SkipTestCertificateCreation,
    [switch]$SkipUvSync
)

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$buildNuitkaScript = Join-Path $root 'build_nuitka.ps1'
$buildMsixScript = Join-Path $root 'build_msix.ps1'
$signMsixScript = Join-Path $root 'sign_msix.ps1'

function Remove-PathIfExists {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Recurse -Force
        Write-Host ('  Removed: ' + $Path)
    }
}

foreach ($required in @($buildNuitkaScript, $buildMsixScript, $signMsixScript)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw ('Required script not found: ' + $required)
    }
}

Push-Location $root
try {
    $entryBaseName = [System.IO.Path]::GetFileNameWithoutExtension($EntryScript)
    if (-not $entryBaseName) {
        throw ('Invalid EntryScript: ' + $EntryScript)
    }

    Write-Host 'Prep: Clean previous artifacts'
    $resolvedOutputMsixPath = Join-Path $root $OutputMsixPath
    $resolvedStageDir = Join-Path $root $StageDir
    $resolvedExportCerPath = Join-Path $root $ExportCerPath
    $inputDistPath = Join-Path $OutputDir ($entryBaseName + '.dist')
    $inputBuildPath = Join-Path $OutputDir ($entryBaseName + '.build')
    $exeFileName = if ($OutputFileName.ToLowerInvariant().EndsWith('.exe')) { $OutputFileName } else { $OutputFileName + '.exe' }
    $inputExePath = Join-Path $OutputDir $exeFileName

    # Always clean package/staging outputs.
    Remove-PathIfExists -Path $resolvedOutputMsixPath
    Remove-PathIfExists -Path $resolvedStageDir
    if (-not $SkipSigning -and $ExportCerPath) {
        Remove-PathIfExists -Path $resolvedExportCerPath
    }

    # For full build, also clean Nuitka outputs.
    if (-not $SkipNuitkaBuild) {
        Remove-PathIfExists -Path (Join-Path $root $inputDistPath)
        Remove-PathIfExists -Path (Join-Path $root $inputBuildPath)
        Remove-PathIfExists -Path (Join-Path $root $inputExePath)
    }

    if (-not $SkipNuitkaBuild) {
        Write-Host 'Step 1/3: Build with Nuitka'

        & $buildNuitkaScript `
            -EntryScript $EntryScript `
            -OutputDir $OutputDir `
            -OutputFileName $OutputFileName `
            -SkipUvSync:$SkipUvSync

        if ($LASTEXITCODE -ne 0) {
            throw ('Nuitka build failed with exit code ' + $LASTEXITCODE)
        }
    } else {
        Write-Host 'Step 1/3: Skip Nuitka build'
    }

    Write-Host 'Step 2/3: Create MSIX package'

    & $buildMsixScript `
        -InputDistPath $inputDistPath `
        -InputExePath $inputExePath `
        -ManifestPath $ManifestPath `
        -OutputMsixPath $OutputMsixPath `
        -StageDir $StageDir `
        -PublisherCN $PublisherCN `
        -IdentityName $IdentityName `
        -PublisherDisplayName $PublisherDisplayName `
        -Version $Version

    if ($LASTEXITCODE -ne 0) {
        throw ('MSIX creation failed with exit code ' + $LASTEXITCODE)
    }

    if ($SkipSigning) {
        Write-Host 'Step 3/3: Skip signing and verification'
        Write-Host ''
        Write-Host 'MSIX package was created successfully (unsigned).'
        Write-Host ('MSIX: ' + (Join-Path $root $OutputMsixPath))
        return
    }

    Write-Host 'Step 3/3: Sign and verify MSIX'

    & $signMsixScript `
        -FilePath $OutputMsixPath `
        -PfxPath $PfxPath `
        -PfxPassword $PfxPassword `
        -Thumbprint $Thumbprint `
        -PublisherCN $PublisherCN `
        -ExportCerPath $ExportCerPath `
        -TimestampServer $TimestampServer `
        -SignToolPath $SignToolPath `
        -SkipTestCertificateCreation:$SkipTestCertificateCreation

    if ($LASTEXITCODE -ne 0) {
        throw ('Signing/verification failed with exit code ' + $LASTEXITCODE)
    }

    Write-Host ''
    Write-Host 'All steps completed successfully.'
    Write-Host ('MSIX: ' + (Join-Path $root $OutputMsixPath))
    if ($ExportCerPath) {
        Write-Host ('CER : ' + (Join-Path $root $ExportCerPath))
    }
}
finally {
    Pop-Location
}