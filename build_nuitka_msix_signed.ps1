# build_nuitka_msix_signed.ps1 - Build with Nuitka, create MSIX, sign, and verify
#
# Default flow:
# 1) Build dist/PandocGUI.exe with Nuitka onefile
# 2) Create MSIX package using build_msix.ps1
# 3) Create a self-signed test certificate (unless disabled)
# 4) Sign and verify MSIX using sign_code.ps1
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
    [switch]$SkipUvSync,
    [switch]$UseClang
)

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$buildMsixScript = Join-Path $root 'build_msix.ps1'
$createCertScript = Join-Path $root 'create_test_certificate.ps1'
$signScript = Join-Path $root 'sign_code.ps1'

function Remove-PathIfExists {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Recurse -Force
        Write-Host ('  Removed: ' + $Path)
    }
}

foreach ($required in @($buildMsixScript, $createCertScript, $signScript)) {
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
        Write-Host 'Step 1/4: Build with Nuitka'

        if (-not $SkipUvSync) {
            & uv sync --group build
            if ($LASTEXITCODE -ne 0) {
                throw ('uv sync failed with exit code ' + $LASTEXITCODE)
            }
        }

        if ($UseClang) {
            $env:CC = 'clang-cl'
            $env:CXX = 'clang-cl'
        }

        $nuitkaOptions = @(
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

        if ($UseClang) {
            $nuitkaOptions = @('--clang', '--msvc=latest') + $nuitkaOptions
        }

        $nuitkaArgs = @('-m', 'nuitka') + $nuitkaOptions
        & uv run python @nuitkaArgs
        if ($LASTEXITCODE -ne 0) {
            throw ('Nuitka build failed with exit code ' + $LASTEXITCODE)
        }
    } else {
        Write-Host 'Step 1/4: Skip Nuitka build'
    }

    Write-Host 'Step 2/4: Create MSIX package'

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
        Write-Host 'Step 3/4: Skip signing certificate preparation'
        Write-Host 'Step 4/4: Skip signing and verification'
        Write-Host ''
        Write-Host 'MSIX package was created successfully (unsigned).'
        Write-Host ('MSIX: ' + (Join-Path $root $OutputMsixPath))
        return
    }

    Write-Host 'Step 3/4: Prepare signing certificate'
    if ($PfxPath) {
        if (-not (Test-Path -LiteralPath $PfxPath)) {
            throw ('PFX file not found: ' + $PfxPath)
        }
        if (-not $PfxPassword) {
            throw 'PfxPassword is required when PfxPath is specified.'
        }
        Write-Host ('Using PFX: ' + $PfxPath)
    } else {
        if ($Thumbprint) {
            Write-Host ('Using certificate thumbprint: ' + $Thumbprint)
        } else {
            if (-not $SkipTestCertificateCreation) {
                & $createCertScript -Subject $PublisherCN
                if ($LASTEXITCODE -ne 0) {
                    throw ('Test certificate creation failed with exit code ' + $LASTEXITCODE)
                }
            } else {
                Write-Host 'Skip test certificate creation. Existing certificate is expected in store.'
            }
        }
    }

    Write-Host 'Step 4/4: Sign and verify MSIX'
    if ($PfxPath) {
        & $signScript `
            -FilePath $OutputMsixPath `
            -PfxPath $PfxPath `
            -PfxPassword $PfxPassword `
            -ExportCerPath $ExportCerPath `
            -TimestampServer $TimestampServer `
            -SignToolPath $SignToolPath
    } elseif ($Thumbprint) {
        & $signScript `
            -FilePath $OutputMsixPath `
            -Thumbprint $Thumbprint `
            -ExportCerPath $ExportCerPath `
            -TimestampServer $TimestampServer `
            -SignToolPath $SignToolPath
    } else {
        & $signScript `
            -FilePath $OutputMsixPath `
            -Subject $PublisherCN `
            -ExportCerPath $ExportCerPath `
            -TimestampServer $TimestampServer `
            -SignToolPath $SignToolPath
    }

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