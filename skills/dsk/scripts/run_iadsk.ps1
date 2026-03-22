[CmdletBinding(PositionalBinding = $false)]
Param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$IadskArgs
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$skillRoot = Split-Path -Parent $scriptDir

$iadskScript = Join-Path $scriptDir "iadsk.py"

if (-not (Test-Path -LiteralPath $iadskScript)) {
    Write-Error "iadsk.py no encontrado en $iadskScript"
    exit 1
}

if ($null -eq $IadskArgs) {
    $IadskArgs = @()
}

if ($IadskArgs.Count -gt 0 -and $IadskArgs[0] -eq "--") {
    if ($IadskArgs.Count -eq 1) {
        $IadskArgs = @()
    } else {
        $IadskArgs = $IadskArgs[1..($IadskArgs.Count - 1)]
    }
}

$pythonCmd = "python3"
$pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $pythonCmd) {
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue | Select-Object -First 1
}
if (-not $pythonCmd) {
    Write-Error "Python 3 no está disponible. Instala Python 3 para usar iadsk.py."
    exit 1
}

& $pythonCmd.Source $iadskScript @IadskArgs
