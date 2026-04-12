[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ArgsList
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ScriptPath = Join-Path $ScriptDir "amstrad_catalog.py"

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 $ScriptPath @ArgsList
    exit $LASTEXITCODE
}

& python $ScriptPath @ArgsList
exit $LASTEXITCODE
