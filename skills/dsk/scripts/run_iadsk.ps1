[CmdletBinding(PositionalBinding = $false)]
Param(
    [string]$Binary,
    [ValidateSet("markdown", "json")]
    [string]$Format = "markdown",
    [switch]$RawJson,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$IadskArgs
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$skillRoot = Split-Path -Parent $scriptDir

$archRaw = [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture.ToString().ToLowerInvariant()
switch ($archRaw) {
    "x64" { $arch = "x64" }
    "arm64" { $arch = "arm64" }
    default { $arch = $archRaw }
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

if ($IadskArgs.Count -eq 0) {
    $IadskArgs = @("help")
}

function Resolve-IadskBinary {
    param([string]$ExplicitPath)

    if (-not [string]::IsNullOrWhiteSpace($ExplicitPath)) {
        if (Test-Path -LiteralPath $ExplicitPath) {
            return (Resolve-Path $ExplicitPath).Path
        }
        throw "Binary not found: $ExplicitPath"
    }

    $cmd = Get-Command iaDSK -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    $defaultBin = Join-Path $env:USERPROFILE "bin/iaDSK.exe"
    if (Test-Path -LiteralPath $defaultBin) {
        return $defaultBin
    }

    $bundled = Join-Path $skillRoot ("assets/bin/windows-{0}/iaDSK.exe" -f $arch)
    if (Test-Path -LiteralPath $bundled) {
        return $bundled
    }

    throw "iaDSK no está disponible para windows-$arch. Ejecuta primero scripts/install_iadsk.ps1 o install_iadsk.sh."
}

function Convert-CellValue {
    param($Value)

    if ($null -eq $Value) {
        return ""
    }
    if ($Value -is [bool]) {
        if ($Value) {
            return "si"
        }
        return "no"
    }
    if ($Value -is [System.Collections.IDictionary] -or ($Value -is [System.Collections.IEnumerable] -and $Value -isnot [string])) {
        return ($Value | ConvertTo-Json -Depth 20 -Compress)
    }
    return [string]$Value
}

function Convert-MarkdownCell {
    param($Value)

    $text = Convert-CellValue $Value
    if ($null -eq $text) {
        return ""
    }

    $text = [string]$text
    $text = $text.Replace("`r`n", "<br>")
    $text = $text.Replace("`n", "<br>")
    $text = $text.Replace("|", "\|")
    return $text
}

function Get-MapPairs {
    param($Map)

    if ($null -eq $Map) {
        return @()
    }

    if ($Map -is [System.Collections.IDictionary]) {
        $pairs = @()
        foreach ($k in $Map.Keys) {
            $pairs += ,([PSCustomObject]@{ Key = [string]$k; Value = $Map[$k] })
        }
        return $pairs
    }

    $objPairs = @()
    foreach ($p in $Map.PSObject.Properties) {
        if ($p.MemberType -in @("NoteProperty", "Property")) {
            $objPairs += ,([PSCustomObject]@{ Key = [string]$p.Name; Value = $p.Value })
        }
    }
    return $objPairs
}

function Has-MapKey {
    param(
        $Map,
        [string]$Key
    )

    foreach ($pair in (Get-MapPairs -Map $Map)) {
        if ($pair.Key -eq $Key) {
            return $true
        }
    }
    return $false
}

function Get-MapValue {
    param(
        $Map,
        [string]$Key
    )

    foreach ($pair in (Get-MapPairs -Map $Map)) {
        if ($pair.Key -eq $Key) {
            return $pair.Value
        }
    }
    return $null
}

function Write-MarkdownTable {
    param(
        [string[]]$Headers,
        [object[]]$Rows
    )

    if ($null -eq $Rows -or $Rows.Count -eq 0) {
        return
    }

    $headerCells = @()
    foreach ($h in $Headers) {
        $headerCells += (Convert-MarkdownCell $h)
    }

    Write-Output ("| {0} |" -f ($headerCells -join " | "))
    Write-Output ("| {0} |" -f ((@("---") * $Headers.Count) -join " | "))

    foreach ($row in $Rows) {
        $cells = @()
        for ($i = 0; $i -lt $Headers.Count; $i++) {
            $cells += (Convert-MarkdownCell $row[$i])
        }
        Write-Output ("| {0} |" -f ($cells -join " | "))
    }

    Write-Output ""
}

function Write-KeyValueTable {
    param(
        [string]$Title,
        $Map,
        [string[]]$PreferredKeys
    )

    Write-Output ("### {0}" -f $Title)

    $keys = New-Object System.Collections.Generic.List[string]
    if ($PreferredKeys) {
        foreach ($k in $PreferredKeys) {
            if (Has-MapKey -Map $Map -Key $k) {
                $keys.Add($k)
            }
        }
    }

    foreach ($pair in (Get-MapPairs -Map $Map)) {
        if (-not $keys.Contains([string]$pair.Key)) {
            $keys.Add([string]$pair.Key)
        }
    }

    $rows = @()
    foreach ($k in $keys) {
        $rows += ,@($k, (Convert-CellValue (Get-MapValue -Map $Map -Key $k)))
    }

    Write-MarkdownTable -Headers @("Campo", "Valor") -Rows $rows
}

function Write-CatMarkdown {
    param($Data)

    Write-Output "### Catalogo"
    Write-Output ('- Disco: `{0}`' -f (Convert-CellValue (Get-MapValue -Map $Data -Key "dsk")))

    $entriesRaw = Get-MapValue -Map $Data -Key "entries"
    $entries = @($entriesRaw)

    if ($entries.Count -eq 0) {
        Write-Output "No hay archivos en el disco."
        Write-Output ""
    } else {
        $rows = @()
        foreach ($entry in $entries) {
            $attrs = ""
            if ($entry.read_only) { $attrs += "R" }
            if ($entry.system) { $attrs += "S" }
            $rows += ,@(
                (Convert-CellValue $entry.name),
                (Convert-CellValue $entry.user),
                ("0x{0:X4}" -f ([int]$entry.load)),
                ("0x{0:X4}" -f ([int]$entry.exec)),
                ("{0} KB" -f (Convert-CellValue $entry.size_kb)),
                $attrs
            )
        }
        Write-MarkdownTable -Headers @("Archivo", "Usuario", "Carga", "Ejec", "Tamano", "Attr") -Rows $rows
    }

    Write-KeyValueTable -Title "Espacio" -Map @{
        total_kb = (Get-MapValue -Map $Data -Key "total_kb")
        used_kb = (Get-MapValue -Map $Data -Key "used_kb")
        free_kb = (Get-MapValue -Map $Data -Key "free_kb")
    } -PreferredKeys @("total_kb", "used_kb", "free_kb")
}

function Write-PayloadMarkdown {
    param($Payload)

    $ok = [bool]$Payload.ok
    $command = [string]$Payload.command
    $data = $Payload.data
    if ($null -eq $data) {
        $data = @{}
    }
    $errors = @($Payload.errors)

    if (-not $ok) {
        Write-Output "### Errores"

        $rows = @()
        foreach ($err in $errors) {
            $rows += ,@((Convert-CellValue $err.code), (Convert-CellValue $err.message))
        }

        if ($rows.Count -gt 0) {
            Write-MarkdownTable -Headers @("Codigo", "Mensaje") -Rows $rows
        } else {
            Write-Output "Error sin detalle."
        }
        return
    }

    switch ($command) {
        "new" {
            Write-KeyValueTable -Title "Resumen" -Map $data -PreferredKeys @("dsk", "total_kb", "used_kb", "free_kb")
            return
        }
        "free" {
            Write-KeyValueTable -Title "Espacio libre" -Map $data -PreferredKeys @("dsk", "total_kb", "used_kb", "free_kb")
            return
        }
        "cat" {
            Write-CatMarkdown -Data $data
            return
        }
        { $_ -in @("save", "get", "era") } {
            Write-KeyValueTable -Title ("Resultado de {0}" -f $command) -Map $data -PreferredKeys @()
            return
        }
        default {
            if (Has-MapKey -Map $data -Key "content") {
                Write-Output "### Contenido"
                Write-Output '```text'
                $content = Convert-CellValue (Get-MapValue -Map $data -Key "content")
                if (-not [string]::IsNullOrEmpty($content)) {
                    Write-Output $content
                }
                Write-Output '```'
                Write-Output ""

                Write-KeyValueTable -Title "Metadatos" -Map @{
                    tipo = (Get-MapValue -Map $data -Key "content_type")
                    lineas = (Get-MapValue -Map $data -Key "line_count")
                    bytes = (Get-MapValue -Map $data -Key "bytes")
                } -PreferredKeys @("tipo", "lineas", "bytes")
                return
            }

            Write-KeyValueTable -Title ("Resultado de {0}" -f $command) -Map $data -PreferredKeys @()
            return
        }
    }
}

try {
    $resolved = Resolve-IadskBinary -ExplicitPath $Binary
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}

$effectiveFormat = $Format
if ($RawJson) {
    $effectiveFormat = "json"
}

$tmpOut = [System.IO.Path]::GetTempFileName()
$tmpErr = [System.IO.Path]::GetTempFileName()

try {
    & $resolved @IadskArgs 1> $tmpOut 2> $tmpErr
    $status = $LASTEXITCODE

    $stdoutText = (Get-Content -LiteralPath $tmpOut -Raw -ErrorAction SilentlyContinue)
    $stderrText = (Get-Content -LiteralPath $tmpErr -Raw -ErrorAction SilentlyContinue)

    if ($effectiveFormat -eq "json") {
        if (-not [string]::IsNullOrWhiteSpace($stdoutText)) {
            Write-Output $stdoutText.TrimEnd()
        }
    } else {
        $rendered = $false
        if (-not [string]::IsNullOrWhiteSpace($stdoutText)) {
            try {
                $payload = $stdoutText | ConvertFrom-Json -Depth 20
                Write-PayloadMarkdown -Payload $payload
                $rendered = $true
            } catch {
                $rendered = $false
            }
        }

        if (-not $rendered -and -not [string]::IsNullOrWhiteSpace($stdoutText)) {
            Write-Output "No se pudo formatear la salida de iaDSK."
        }
    }

    if (-not [string]::IsNullOrWhiteSpace($stderrText)) {
        [Console]::Error.Write($stderrText)
    }

    exit $status
} finally {
    Remove-Item -LiteralPath $tmpOut -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $tmpErr -ErrorAction SilentlyContinue
}
