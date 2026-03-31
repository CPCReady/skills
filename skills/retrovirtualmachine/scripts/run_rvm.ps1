[CmdletBinding(PositionalBinding = $false)]
Param(
    [string]$Machine,
    [switch]$Warp,
    [switch]$NoShader,
    [string]$Command,
    [int]$Width,
    [switch]$Play,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RvmArgs
)

$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# run_rvm.ps1 — Wrapper para Retro Virtual Machine 2 (Amstrad CPC) - Windows
#
# Requisito: Variable de entorno RETRO_VIRTUAL_MACHINE_PATH apuntando al
# binario de RVM v2.0 BETA-1 r7.
# ---------------------------------------------------------------------------

$RequiredVersion = "v2.0 BETA-1 r7"

# ---------------------------------------------------------------------------
# 1. Verificar variable de entorno
# ---------------------------------------------------------------------------
if ([string]::IsNullOrWhiteSpace($env:RETRO_VIRTUAL_MACHINE_PATH)) {
    Write-Error "ERROR: Variable de entorno RETRO_VIRTUAL_MACHINE_PATH no definida."
    Write-Error 'Ejemplo: $env:RETRO_VIRTUAL_MACHINE_PATH = "C:\Program Files\Retro Virtual Machine 2\rvm2.exe"'
    exit 1
}

$RvmBin = $env:RETRO_VIRTUAL_MACHINE_PATH

if (-not (Test-Path -LiteralPath $RvmBin)) {
    Write-Error "ERROR: Binario de RVM no encontrado en: $RvmBin"
    exit 1
}

# ---------------------------------------------------------------------------
# 2. Verificar versión
# RVM emite códigos de escape ANSI — se eliminan antes de comparar
# La versión aparece en las primeras líneas del output de --help
# ---------------------------------------------------------------------------
$VersionBlock = (& $RvmBin --help 2>&1 | Select-Object -First 5 | ForEach-Object { $_.ToString() }) -join " "
$VersionClean = $VersionBlock -replace '\x1b\[[0-9;]*m', ''

if ($VersionClean -notlike "*$RequiredVersion*") {
    Write-Error "ERROR: Versión de Retro Virtual Machine no compatible."
    Write-Error "  Requerida : $RequiredVersion"
    Write-Error "  Detectada : $VersionClean"
    exit 1
}

# ---------------------------------------------------------------------------
# 3. Procesar argumentos pass-through (--)
# ---------------------------------------------------------------------------
$PassThrough = $false
$ExtraArgs = @()
$InputFile = ""

if ($null -ne $RvmArgs -and $RvmArgs.Count -gt 0) {
    if ($RvmArgs[0] -eq "--") {
        $PassThrough = $true
        if ($RvmArgs.Count -gt 1) {
            $ExtraArgs = $RvmArgs[1..($RvmArgs.Count - 1)]
        }
    } else {
        # El último argumento no-flag se trata como archivo
        foreach ($arg in $RvmArgs) {
            if (-not $arg.StartsWith("-")) {
                $InputFile = $arg
            } else {
                $ExtraArgs += $arg
            }
        }
    }
}

# Acumular flags opcionales en ExtraArgs
if ($Warp)     { $ExtraArgs += "--warp" }
if ($NoShader) { $ExtraArgs += "--noshader" }
if ($Play)     { $ExtraArgs += "--play" }
if (-not [string]::IsNullOrWhiteSpace($Command)) {
    # Añadir retorno de carro al final del comando si no lo tiene ya
    $CmdValue = $Command
    if (-not $CmdValue.EndsWith("`n")) {
        $CmdValue = $CmdValue + "`n"
    }
    $ExtraArgs += "--command=$CmdValue"
}
if ($Width -gt 0) { $ExtraArgs += "--width=$Width" }

# ---------------------------------------------------------------------------
# 4. Helper: verificar modo interactivo
# ---------------------------------------------------------------------------
function Require-Interactive {
    param([string]$Context)
    if ([Console]::IsInputRedirected) {
        Write-Error "ERROR: $Context requiere un terminal interactivo."
        Write-Error "Proporciona los parámetros necesarios explícitamente."
        exit 1
    }
}

# ---------------------------------------------------------------------------
# 5. Helper: preguntar máquina
# ---------------------------------------------------------------------------
function Prompt-Machine {
    Require-Interactive "Selección de máquina CPC"
    Write-Host ""
    Write-Host "### Máquina CPC"
    Write-Host ""
    Write-Host "  1) cpc464   - Amstrad CPC 464 (cassette, 64K RAM)"
    Write-Host "  2) cpc664   - Amstrad CPC 664 (disco, 64K RAM)"
    Write-Host "  3) cpc6128  - Amstrad CPC 6128 (disco, 128K RAM)"
    Write-Host ""

    while ($true) {
        $selection = Read-Host "Selecciona máquina [1-3]"
        switch ($selection) {
            { $_ -in "1", "cpc464"  } { return "cpc464"  }
            { $_ -in "2", "cpc664"  } { return "cpc664"  }
            { $_ -in "3", "cpc6128" } { return "cpc6128" }
            default { Write-Host "Selección inválida. Elige 1, 2 o 3." }
        }
    }
}

# ---------------------------------------------------------------------------
# 6. Helper: preguntar dirección hexadecimal
# ---------------------------------------------------------------------------
function Prompt-Address {
    param(
        [string]$Label,
        [bool]$Optional = $false
    )
    Write-Host ""
    if ($Optional) {
        $value = Read-Host "$Label (hexadecimal, dejar vacío para omitir)"
        return $value
    } else {
        while ($true) {
            $value = Read-Host "$Label (hexadecimal)"
            if (-not [string]::IsNullOrWhiteSpace($value)) {
                return $value
            }
            Write-Host "ERROR: $Label es obligatoria."
        }
    }
}

# ---------------------------------------------------------------------------
# 7. Determinar tipo de archivo y construir argumentos RVM
# ---------------------------------------------------------------------------
$FinalArgs = @()

if ($PassThrough) {
    # Modo pass-through: argumentos directos a RVM
    if ([string]::IsNullOrWhiteSpace($Machine)) {
        $Machine = Prompt-Machine
    }
    $FinalArgs += "--boot=$Machine"
    $FinalArgs += $ExtraArgs
} elseif ([string]::IsNullOrWhiteSpace($InputFile)) {
    # Sin archivo: arrancar máquina standalone
    if ([string]::IsNullOrWhiteSpace($Machine)) {
        $Machine = Prompt-Machine
    }
    $FinalArgs += "--boot=$Machine"
    $FinalArgs += $ExtraArgs
} else {
    # Con archivo: detectar por extensión
    if (-not (Test-Path -LiteralPath $InputFile)) {
        Write-Error "ERROR: Archivo no encontrado: $InputFile"
        exit 1
    }

    $Ext = [System.IO.Path]::GetExtension($InputFile).ToLowerInvariant().TrimStart(".")

    switch ($Ext) {

        "dsk" {
            if ([string]::IsNullOrWhiteSpace($Machine)) { $Machine = "cpc6128" }
            $FinalArgs += "--boot=$Machine"
            $FinalArgs += "--insert"
            $FinalArgs += $InputFile
            $FinalArgs += $ExtraArgs
        }

        { $_ -in "cdt", "tzx" } {
            if ([string]::IsNullOrWhiteSpace($Machine)) { $Machine = "cpc464" }
            $FinalArgs += "--boot=$Machine"
            $FinalArgs += "--insert"
            $FinalArgs += $InputFile
            $FinalArgs += $ExtraArgs
        }

        "bin" {
            if ([string]::IsNullOrWhiteSpace($Machine)) {
                $Machine = Prompt-Machine
            }
            Require-Interactive "Carga de archivo binario"

            Write-Host ""
            Write-Host "### Cargar archivo binario"
            Write-Host ""
            Write-Host "Archivo: $InputFile"
            Write-Host "Para archivos binarios es OBLIGATORIO indicar la dirección de carga y de salto."

            $LoadAddr = Prompt-Address -Label "Dirección de carga (--load)"
            $JumpAddr = Prompt-Address -Label "Dirección de salto (--jump)"

            $FinalArgs += "--boot=$Machine"
            $FinalArgs += "--load=$LoadAddr"
            $FinalArgs += $InputFile
            $FinalArgs += "--jump=$JumpAddr"
            $FinalArgs += $ExtraArgs
        }

        { $_ -in "sna", "z80" } {
            if ([string]::IsNullOrWhiteSpace($Machine)) {
                $Machine = Prompt-Machine
            }
            $FinalArgs += "--boot=$Machine"
            $FinalArgs += "--snapshot"
            $FinalArgs += $InputFile
            $FinalArgs += $ExtraArgs
        }

        default {
            Write-Error "ERROR: Extensión de archivo no reconocida: .$Ext"
            Write-Error "Tipos soportados: .dsk, .cdt, .tzx, .bin, .sna, .z80"
            Write-Error "Usa -- para pasar argumentos directamente a RVM."
            exit 1
        }
    }
}

# ---------------------------------------------------------------------------
# 8. Verificar instancias abiertas de RVM
# ---------------------------------------------------------------------------
$RvmBinaryName = [System.IO.Path]::GetFileNameWithoutExtension($RvmBin)
$RunningInstances = Get-Process -Name $RvmBinaryName -ErrorAction SilentlyContinue

if ($null -ne $RunningInstances -and $RunningInstances.Count -gt 0) {
    $PidCount = $RunningInstances.Count
    if (-not [Console]::IsInputRedirected) {
        Write-Host ""
        Write-Host "### Instancias de RVM en ejecución: $PidCount"
        Write-Host ""
        foreach ($proc in $RunningInstances) {
            Write-Host "  PID $($proc.Id)"
        }
        Write-Host ""
        $CloseExisting = Read-Host "¿Cerrar instancias existentes antes de lanzar? (s/n) [n]"
        if ([string]::IsNullOrWhiteSpace($CloseExisting)) { $CloseExisting = "n" }
        if ($CloseExisting -in @("s", "S", "y", "Y")) {
            foreach ($proc in $RunningInstances) {
                Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            }
            Write-Host ""
        }
    }
}

# ---------------------------------------------------------------------------
# 9. Lanzar RVM en background
# ---------------------------------------------------------------------------
Start-Process -FilePath $RvmBin -ArgumentList $FinalArgs -WindowStyle Normal

exit 0
