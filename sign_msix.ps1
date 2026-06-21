# sign_msix.ps1 - Prepare signing certificate and sign/verify MSIX package
#
# This script handles the complete signing flow:
# 1) Ensure a signing certificate is available (create test cert if needed)
# 2) Sign the MSIX package
# 3) Verify the signature
#
# Certificate priority:
# 1) If PfxPath is provided, use that PFX file
# 2) Else if Thumbprint is provided, use that certificate from the store
# 3) Else create a self-signed test certificate (unless SkipTestCertificateCreation is set)
#
# Usage examples:
#   ./sign_msix.ps1 -FilePath dist/PandocGUI.msix
#   ./sign_msix.ps1 -FilePath dist/PandocGUI.msix -PfxPath ./cert.pfx -PfxPassword (Read-Host "password" -AsSecureString)
#   ./sign_msix.ps1 -FilePath dist/PandocGUI.msix -Thumbprint "ABCD1234..."
#   ./sign_msix.ps1 -FilePath dist/PandocGUI.msix -PublisherCN "CN=MyName"

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$FilePath,
    
    [string]$PfxPath,
    [securestring]$PfxPassword,
    [string]$Thumbprint,
    [string]$PublisherCN = 'CN=YourName',
    [string]$ExportCerPath = 'dist/PandocGUI.cer',
    [string]$TimestampServer = 'http://timestamp.digicert.com',
    [string]$SignToolPath,
    [switch]$SkipTestCertificateCreation,
    
    # Test certificate parameters
    [string]$CertFriendlyName = 'PandocGUI Test Certificate',
    [int]$CertYearsValid = 3
)

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$signScript = Join-Path $root 'sign_code.ps1'

if (-not (Test-Path -LiteralPath $signScript)) {
    throw ('Required script not found: ' + $signScript)
}

if (-not (Test-Path -LiteralPath $FilePath)) {
    throw ('MSIX file not found: ' + $FilePath)
}

function Ensure-ParentDirectory {
    param([Parameter(Mandatory = $true)][string]$Path)

    $parent = Split-Path -Parent $Path
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
}

function Add-CertificateToStore {
    param(
        [Parameter(Mandatory = $true)]
        [System.Security.Cryptography.X509Certificates.X509Certificate2]$Certificate,

        [Parameter(Mandatory = $true)]
        [ValidateSet('Root', 'TrustedPeople')]
        [string]$StoreName
    )

    $store = New-Object System.Security.Cryptography.X509Certificates.X509Store($StoreName, 'CurrentUser')
    try {
        $store.Open([System.Security.Cryptography.X509Certificates.OpenFlags]::ReadWrite)
        $existing = $store.Certificates.Find(
            [System.Security.Cryptography.X509Certificates.X509FindType]::FindByThumbprint,
            $Certificate.Thumbprint,
            $false
        )

        if ($existing.Count -gt 0) {
            Write-Host ('Already trusted in Cert:\CurrentUser\' + $StoreName + ': ' + $Certificate.Thumbprint)
            return
        }

        $store.Add($Certificate)
        Write-Host ('Added certificate to Cert:\CurrentUser\' + $StoreName + ': ' + $Certificate.Thumbprint)
    }
    finally {
        $store.Close()
    }
}

function New-TestCertificate {
    param(
        [string]$Subject,
        [string]$FriendlyName,
        [int]$YearsValid,
        [string]$ExportCerPath
    )

    if ($YearsValid -lt 1) {
        throw 'YearsValid must be 1 or greater.'
    }

    $notAfter = (Get-Date).AddYears($YearsValid)
    $certStoreLocation = 'Cert:\CurrentUser\My'

    $cert = New-SelfSignedCertificate `
        -Type Custom `
        -Subject $Subject `
        -FriendlyName $FriendlyName `
        -KeyAlgorithm RSA `
        -KeyLength 2048 `
        -HashAlgorithm SHA256 `
        -KeyUsage DigitalSignature `
        -CertStoreLocation $certStoreLocation `
        -NotAfter $notAfter `
        -TextExtension @(
            '2.5.29.37={text}1.3.6.1.5.5.7.3.3',
            '2.5.29.19={text}'
        )

    Write-Host 'Created test code-signing certificate:'
    Write-Host ('  Subject    : ' + $cert.Subject)
    Write-Host ('  Thumbprint : ' + $cert.Thumbprint)
    Write-Host ('  Expires    : ' + $cert.NotAfter.ToString('u'))
    Write-Host ('  Store      : ' + $certStoreLocation)

    if ($ExportCerPath) {
        Ensure-ParentDirectory -Path $ExportCerPath
        Export-Certificate -Cert $cert -FilePath $ExportCerPath -Force | Out-Null
        Write-Host ('Exported CER: ' + $ExportCerPath)
    }

    return $cert
}

Push-Location $root
try {
    Write-Host 'Step 1/2: Prepare signing certificate'
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
                $cert = New-TestCertificate -Subject $PublisherCN -FriendlyName $CertFriendlyName -YearsValid $CertYearsValid -ExportCerPath $ExportCerPath
            } else {
                Write-Host 'Skip test certificate creation. Existing certificate is expected in store.'
            }
        }
    }

    Write-Host 'Step 2/2: Sign and verify MSIX'
    if ($PfxPath) {
        & $signScript `
            -FilePath $FilePath `
            -PfxPath $PfxPath `
            -PfxPassword $PfxPassword `
            -ExportCerPath $ExportCerPath `
            -TimestampServer $TimestampServer `
            -SignToolPath $SignToolPath
    } elseif ($Thumbprint) {
        & $signScript `
            -FilePath $FilePath `
            -Thumbprint $Thumbprint `
            -ExportCerPath $ExportCerPath `
            -TimestampServer $TimestampServer `
            -SignToolPath $SignToolPath
    } else {
        & $signScript `
            -FilePath $FilePath `
            -Subject $PublisherCN `
            -ExportCerPath $ExportCerPath `
            -TimestampServer $TimestampServer `
            -SignToolPath $SignToolPath
    }

    if ($LASTEXITCODE -ne 0) {
        throw ('Signing/verification failed with exit code ' + $LASTEXITCODE)
    }

    Write-Host ''
    Write-Host 'Signing completed successfully.'
    Write-Host ('MSIX: ' + (Join-Path $root $FilePath))
    if ($ExportCerPath) {
        Write-Host ('CER : ' + (Join-Path $root $ExportCerPath))
    }
}
finally {
    Pop-Location
}
