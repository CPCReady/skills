[CmdletBinding(PositionalBinding = $false)]
Param()
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $ScriptDir ".venv"

if (-Not (Test-Path $VenvDir)) {
    Write-Host "Instalando dependencias de m4board en un entorno virtual aislado..."
    python3 -m venv $VenvDir
    $PipExe = Join-Path $VenvDir "Scripts\pip.exe"
    if (-Not (Test-Path $PipExe)) { $PipExe = Join-Path $VenvDir "bin\pip" }
    & $PipExe install --quiet -r (Join-Path $ScriptDir "requirements.txt")
}

$PythonExe = Join-Path $VenvDir "Scripts\python.exe"
if (-Not (Test-Path $PythonExe)) {
    $PythonExe = Join-Path $VenvDir "bin\python"
}

# Pass args
& $PythonExe (Join-Path $ScriptDir "m4board.py") $args
