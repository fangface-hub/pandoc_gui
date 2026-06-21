# create_test_certificate.ps1 - Create a self-signed test code-signing certificate
#
# Usage examples:
#   ./create_test_certificate.ps1
#   ./create_test_certificate.ps1 -Subject "CN=YourName"
#   ./create_test_certificate.ps1 -ExportCerPath ./certificate.cer
#   ./create_test_certificate.ps1 -ExportPfxPath ./certificate.pfx -PfxPassword (Read-Host "PFX password" -AsSecureString)
#   ./create_test_certificate.ps1 -InstallToTrustedPeople -InstallToRoot

[CmdletBinding()]
param(
    [string]$Subject = 'CN=YourName',
    [string]$FriendlyName = 'PandocGUI Test Certificate',
    [int]$YearsValid = 3,
    [string]$CertStoreLocation = 'Cert:\CurrentUser\My',
    [string]$ExportCerPath,
    [string]$ExportPfxPath,
    [securestring]$PfxPassword,
    [switch]$InstallToTrustedPeople,
    [switch]$InstallToRoot
)

$ErrorActionPreference = 'Stop'

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

if ($YearsValid -lt 1) {
    throw 'YearsValid must be 1 or greater.'
}

if ($ExportPfxPath -and -not $PfxPassword) {
    throw 'PfxPassword is required when ExportPfxPath is specified.'
}

$notAfter = (Get-Date).AddYears($YearsValid)

$cert = New-SelfSignedCertificate `
    -Type Custom `
    -Subject $Subject `
    -FriendlyName $FriendlyName `
    -KeyAlgorithm RSA `
    -KeyLength 2048 `
    -HashAlgorithm SHA256 `
    -KeyUsage DigitalSignature `
    -CertStoreLocation $CertStoreLocation `
    -NotAfter $notAfter `
    -TextExtension @(
        '2.5.29.37={text}1.3.6.1.5.5.7.3.3',
        '2.5.29.19={text}'
    )

Write-Host 'Created test code-signing certificate:'
Write-Host ('  Subject    : ' + $cert.Subject)
Write-Host ('  Thumbprint : ' + $cert.Thumbprint)
Write-Host ('  Expires    : ' + $cert.NotAfter.ToString('u'))
Write-Host ('  Store      : ' + $CertStoreLocation)

if ($ExportCerPath) {
    Ensure-ParentDirectory -Path $ExportCerPath
    Export-Certificate -Cert $cert -FilePath $ExportCerPath -Force | Out-Null
    Write-Host ('Exported CER: ' + $ExportCerPath)
}

if ($ExportPfxPath) {
    Ensure-ParentDirectory -Path $ExportPfxPath
    Export-PfxCertificate -Cert $cert -FilePath $ExportPfxPath -Password $PfxPassword -Force | Out-Null
    Write-Host ('Exported PFX: ' + $ExportPfxPath)
}

if ($InstallToTrustedPeople) {
    Add-CertificateToStore -Certificate $cert -StoreName 'TrustedPeople'
}

if ($InstallToRoot) {
    Add-CertificateToStore -Certificate $cert -StoreName 'Root'
}

Write-Host ''
Write-Host 'Note:'
Write-Host '  For MSIX packaging, AppxManifest.xml Identity Publisher must match certificate subject.'