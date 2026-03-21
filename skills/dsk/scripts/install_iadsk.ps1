Param(
    [string]$InstallDir,
    [switch]$Json
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$skillRoot = Split-Path -Parent $scriptDir

$archRaw = [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture.ToString().ToLower()
switch ($archRaw) {
    "x64" { $arch = "x64" }
    "arm64" { $arch = "arm64" }
    default { $arch = $archRaw }
}

$platform = "windows"
$binaryName = "iaDSK.exe"

if ([string]::IsNullOrWhiteSpace($InstallDir)) {
    $InstallDir = Join-Path $env:USERPROFILE "bin"
}

$sourceBinary = Join-Path $skillRoot ("assets/bin/{0}-{1}/{2}" -f $platform, $arch, $binaryName)
if (-not (Test-Path -LiteralPath $sourceBinary)) {
    $msg = "No bundled iaDSK binary for $platform-$arch. Expected: $sourceBinary"
    if ($Json) {
        @{ ok = $false; system = $platform; arch = $arch; error = $msg } | ConvertTo-Json -Compress | Write-Error
    } else {
        Write-Error $msg
    }
    exit 1
}

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
$installedBinary = Join-Path $InstallDir $binaryName
Copy-Item -LiteralPath $sourceBinary -Destination $installedBinary -Force

if ($Json) {
    @{ ok = $true; system = $platform; arch = $arch; source_binary = $sourceBinary; installed_binary = $installedBinary } | ConvertTo-Json -Compress
} else {
    Write-Output "iaDSK instalado en: $installedBinary"
}
