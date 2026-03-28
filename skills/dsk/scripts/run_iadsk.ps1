[CmdletBinding(PositionalBinding = $false)]
Param(
    [string]$Binary,
    [ValidateSet("markdown", "json")]
    [string]$Format = "json",
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

    throw "iaDSK is not available for windows-$arch. Run scripts/install_iadsk.ps1 or install_iadsk.sh first."
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

    Write-MarkdownTable -Headers @("Field", "Value") -Rows $rows
}

function Format-KbValue {
    param($Value)
    
    if ($null -eq $Value -or $Value -eq "") {
        return ""
    }
    return "$Value KB"
}

function Write-CatMarkdown {
    param($Data)

    Write-Output "### Catalog"
    Write-Output ('- Disk: `{0}`' -f (Convert-CellValue (Get-MapValue -Map $Data -Key "dsk")))

    $entriesRaw = Get-MapValue -Map $Data -Key "entries"
    $entries = @($entriesRaw)

    if ($entries.Count -eq 0) {
        Write-Output "No files on disk."
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
        Write-MarkdownTable -Headers @("File", "User", "Load", "Exec", "Size", "Attr") -Rows $rows
    }

    Write-KeyValueTable -Title "Space" -Map @{
        total_kb = (Format-KbValue (Get-MapValue -Map $Data -Key "total_kb"))
        used_kb = (Format-KbValue (Get-MapValue -Map $Data -Key "used_kb"))
        free_kb = (Format-KbValue (Get-MapValue -Map $Data -Key "free_kb"))
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
        Write-Output "### Errors"

        $rows = @()
        foreach ($err in $errors) {
            $rows += ,@((Convert-CellValue $err.code), (Convert-CellValue $err.message))
        }

        if ($rows.Count -gt 0) {
            Write-MarkdownTable -Headers @("Code", "Message") -Rows $rows
        } else {
            Write-Output "Error without details."
        }
        return
    }

    switch ($command) {
        "new" {
            Write-KeyValueTable -Title "Summary" -Map @{
                dsk = (Get-MapValue -Map $data -Key "dsk")
                total_kb = (Format-KbValue (Get-MapValue -Map $data -Key "total_kb"))
                used_kb = (Format-KbValue (Get-MapValue -Map $data -Key "used_kb"))
                free_kb = (Format-KbValue (Get-MapValue -Map $data -Key "free_kb"))
            } -PreferredKeys @("dsk", "total_kb", "used_kb", "free_kb")
            return
        }
        "free" {
            Write-KeyValueTable -Title "Free Space" -Map @{
                dsk = (Get-MapValue -Map $data -Key "dsk")
                total_kb = (Format-KbValue (Get-MapValue -Map $data -Key "total_kb"))
                used_kb = (Format-KbValue (Get-MapValue -Map $data -Key "used_kb"))
                free_kb = (Format-KbValue (Get-MapValue -Map $data -Key "free_kb"))
            } -PreferredKeys @("dsk", "total_kb", "used_kb", "free_kb")
            return
        }
        "cat" {
            Write-CatMarkdown -Data $data
            return
        }
        { $_ -in @("save", "get", "era") } {
            Write-KeyValueTable -Title ("Result: {0}" -f $command) -Map $data -PreferredKeys @()
            return
        }
        default {
            if (Has-MapKey -Map $data -Key "content") {
                Write-Output "### Content"
                Write-Output '```text'
                $content = Convert-CellValue (Get-MapValue -Map $data -Key "content")
                if (-not [string]::IsNullOrEmpty($content)) {
                    Write-Output $content
                }
                Write-Output '```'
                Write-Output ""

                # METADATA TABLE - Commented out but can be re-enabled
                # Uncomment the lines below to show content metadata
                # Write-KeyValueTable -Title "Metadata" -Map @{
                #     type = (Get-MapValue -Map $data -Key "content_type")
                #     encoding = (Get-MapValue -Map $data -Key "encoding")
                #     lines = (Get-MapValue -Map $data -Key "line_count")
                #     bytes = (Get-MapValue -Map $data -Key "bytes")
                # } -PreferredKeys @("type", "encoding", "lines", "bytes")
                return
            }

            Write-KeyValueTable -Title ("Result: {0}" -f $command) -Map $data -PreferredKeys @()
            return
        }
    }
}

function Test-BinaryFile {
    param([string]$FilePath)

    if (-not (Test-Path -LiteralPath $FilePath)) {
        return $false
    }

    try {
        $mime = (Get-Content -LiteralPath $FilePath -Raw -TotalCount 8000 -ErrorAction SilentlyContinue)
        if ($mime -match '[^\x09\x0A\x0D\x20-\x7E]') {
            return $true
        }
    } catch {}

    $ext = [System.IO.Path]::GetExtension($FilePath).ToLowerInvariant()
    $textExts = @(".bas", ".txt", ".asm", ".s", ".inc", ".h", ".c", ".py", ".json")
    if ($ext -in $textExts) {
        return $false
    }

    return $true
}

function Invoke-DskNamePrompt {
    param([string]$Command)
    
    # Check if --dsk argument is present
    $hasDsk = $false
    for ($i = 0; $i -lt $IadskArgs.Count; $i++) {
        if ($IadskArgs[$i] -eq "--dsk") {
            $hasDsk = $true
            break
        }
    }
    
    if ($hasDsk) {
        return
    }
    
    # Check if running in interactive mode
    if ([Console]::IsInputRedirected) {
        Write-Error "ERROR: El comando '$Command' requiere --dsk <nombre.dsk>`nEjemplo: --dsk demo.dsk"
        exit 1
    }
    
    # Prompt for DSK name
    Write-Output ""
    Write-Output "### Nombre de imagen DSK"
    Write-Output ""
    
    $dskName = ""
    while ($true) {
        $dskName = Read-Host "Nombre del archivo DSK"
        if (-not [string]::IsNullOrWhiteSpace($dskName)) {
            # Add .dsk extension if not present
            if ($dskName -notmatch '\.dsk$') {
                $dskName = "$dskName.dsk"
            }
            break
        }
        Write-Output ""
        Write-Output "⚠️  El nombre del archivo DSK es OBLIGATORIO. Por favor, ingresa un valor."
        Write-Output ""
    }
    
    # Insert --dsk argument into IadskArgs array
    $newArgs = @()
    $newArgs += $IadskArgs[0]  # command (save, new, cat, etc.)
    $newArgs += "--dsk"
    $newArgs += $dskName
    # Add remaining args
    for ($i = 1; $i -lt $IadskArgs.Count; $i++) {
        $newArgs += $IadskArgs[$i]
    }
    $script:IadskArgs = $newArgs
}

function Invoke-BinaryLoadPrompt {
    param([string]$FilePath)

    Write-Output ""
    Write-Output "--- Añadir archivo binario ---"
    Write-Output "Archivo: $FilePath"
    Write-Output "Para archivos binarios es OBLIGATORIO indicar la dirección de carga AMSDOS."
    Write-Output ""

    while ($true) {
        $loadInput = Read-Host "Dirección de carga (--load) en hexadecimal"
        if (-not [string]::IsNullOrWhiteSpace($loadInput)) {
            return $loadInput
        }
        Write-Output ""
        Write-Output "ERROR: La dirección de carga es obligatoria para archivos binarios."
        Write-Output ""
    }
}

function Invoke-ExecAddressPrompt {
    param([string]$FilePath)

    Write-Output ""
    Write-Output "Dirección de ejecución (--exec) en hexadecimal."
    Write-Output "OBLIGATORIO para programas ejecutables. Dejar vacío solo para datos."
    Write-Output ""

    $execInput = Read-Host "Dirección de ejecución (--exec)"
    return $execInput
}

function Invoke-FileTypePrompt {
    param([string]$FilePath, [bool]$IsBinary)

    Write-Output ""
    Write-Output "Tipo de archivo AMSDOS:"
    Write-Output "  1) ascii   - Archivo de texto ASCII"
    Write-Output "  2) binary  - Archivo binario con cabecera AMSDOS"
    Write-Output "  3) raw     - Datos crudos sin cabecera"
    Write-Output ""

    if ($IsBinary) {
        $typeInput = Read-Host "Selecciona tipo [2]"
        if ([string]::IsNullOrWhiteSpace($typeInput)) {
            $typeInput = "2"
        }
    } else {
        $typeInput = Read-Host "Selecciona tipo [1]"
        if ([string]::IsNullOrWhiteSpace($typeInput)) {
            $typeInput = "1"
        }
    }

    switch ($typeInput) {
        "1" { return "ascii" }
        "2" { return "binary" }
        "3" { return "raw" }
        default { return "binary" }
    }
}

function Test-FileExistsInDsk {
    param([string]$DskPath, [string]$FileName, [string]$BinaryPath)

    if (-not (Test-Path -LiteralPath $DskPath)) {
        return $false
    }

    $tmpCat = [System.IO.Path]::GetTempFileName()
    try {
        & $BinaryPath "cat" "--dsk" $DskPath 1> $tmpCat 2> $null
        if ($LASTEXITCODE -ne 0) {
            return $false
        }

        $catJson = Get-Content -LiteralPath $tmpCat -Raw
        $filenameUpper = [System.IO.Path]::GetFileName($FileName).ToUpperInvariant()

        if ($catJson -match "`"name`":`"$filenameUpper`"") {
            return $true
        }

        return $false
    } catch {
        return $false
    } finally {
        Remove-Item -LiteralPath $tmpCat -ErrorAction SilentlyContinue
    }
}

function Invoke-OverwritePrompt {
    param([string]$FileName)

    Write-Output ""
    Write-Output "⚠️  El archivo '$FileName' ya existe en el disco."
    Write-Output ""

    $overwrite = Read-Host "¿Deseas sobrescribir? (s/n) [n]"
    if ([string]::IsNullOrWhiteSpace($overwrite)) {
        $overwrite = "n"
    }

    return ($overwrite -match "^[sySY]$")
}

function Get-ArgIndex {
    param([string[]]$Args, [string]$Flag)

    for ($i = 0; $i -lt $Args.Count; $i++) {
        if ($Args[$i] -eq $Flag) {
            return $i
        }
    }
    return -1
}

function Invoke-SaveCommandCheck {
    $cmdIndex = -1
    for ($i = 0; $i -lt $IadskArgs.Count; $i++) {
        if ($IadskArgs[$i] -eq "save" -or $IadskArgs[$i] -eq "import") {
            $cmdIndex = $i
            break
        }
    }

    if ($cmdIndex -eq -1) {
        return
    }

    $fileIndex = Get-ArgIndex -Args $IadskArgs -Flag "--file"
    if ($fileIndex -eq -1 -or $fileIndex + 1 -ge $IadskArgs.Count) {
        return
    }

    $filePath = $IadskArgs[$fileIndex + 1]
    if (-not (Test-Path -LiteralPath $filePath)) {
        return
    }

    $hasLoad = (Get-ArgIndex -Args $IadskArgs -Flag "--load") -ne -1
    $hasExec = (Get-ArgIndex -Args $IadskArgs -Flag "--exec") -ne -1
    $hasType = (Get-ArgIndex -Args $IadskArgs -Flag "--type") -ne -1
    $isInteractive = [Environment]::UserInteractive

    $isBinary = Test-BinaryFile -FilePath $filePath

    # Step 1: Prompt for file type if not specified
    if (-not $hasType -and $isInteractive) {
        Write-Output ""
        $fileType = Invoke-FileTypePrompt -FilePath $filePath -IsBinary $isBinary
        $IadskArgs += @("--type", $fileType)
    }

    # Step 2: For binary files, require load address
    if ($isBinary -and (-not $hasLoad)) {
        if ($isInteractive) {
            Write-Output ""
            Write-Output "[run_iadsk.ps1] Detectado archivo binario sin dirección de carga."
            $loadAddr = Invoke-BinaryLoadPrompt -FilePath $filePath
            $IadskArgs += @("--load", $loadAddr)
        } else {
            [Console]::Error.WriteLine("ERROR: Archivos binarios requieren --load <dirección>.")
            [Console]::Error.WriteLine("Ejemplo: --load 0x4000")
            exit 1
        }
    }

    # Step 3: For binary files, prompt for exec address if not specified
    if ($isBinary -and (-not $hasExec) -and $isInteractive) {
        $execAddr = Invoke-ExecAddressPrompt -FilePath $filePath
        if (-not [string]::IsNullOrWhiteSpace($execAddr)) {
            $IadskArgs += @("--exec", $execAddr)
        }
        Write-Output ""
    }
}

function Invoke-OverwriteCheck {
    param([string]$ResolvedBinary)

    $cmdIndex = -1
    for ($i = 0; $i -lt $IadskArgs.Count; $i++) {
        if ($IadskArgs[$i] -eq "save" -or $IadskArgs[$i] -eq "import") {
            $cmdIndex = $i
            break
        }
    }

    if ($cmdIndex -eq -1) {
        return
    }

    $fileIndex = Get-ArgIndex -Args $IadskArgs -Flag "--file"
    if ($fileIndex -eq -1 -or $fileIndex + 1 -ge $IadskArgs.Count) {
        return
    }

    $dskIndex = Get-ArgIndex -Args $IadskArgs -Flag "--dsk"
    if ($dskIndex -eq -1 -or $dskIndex + 1 -ge $IadskArgs.Count) {
        return
    }

    $hasForce = (Get-ArgIndex -Args $IadskArgs -Flag "--force") -ne -1
    if ($hasForce) {
        return
    }

    $isInteractive = [Environment]::UserInteractive
    if (-not $isInteractive) {
        return
    }

    $filePath = $IadskArgs[$fileIndex + 1]
    $dskPath = $IadskArgs[$dskIndex + 1]
    $fileName = [System.IO.Path]::GetFileName($filePath)

    if (Test-FileExistsInDsk -DskPath $dskPath -FileName $fileName -BinaryPath $ResolvedBinary) {
        if (Invoke-OverwritePrompt -FileName $fileName) {
            $IadskArgs += @("--force")
        } else {
            Write-Output ""
            Write-Output "Operación cancelada por el usuario."
            exit 0
        }
    }
}

# Check if DSK name is required and prompt if missing
if ($IadskArgs.Count -gt 0) {
    $command = $IadskArgs[0]
    switch ($command) {
        { $_ -in @("help", "--help", "-h") } {
            # help doesn't need --dsk
        }
        default {
            # All other commands need --dsk
            Invoke-DskNamePrompt -Command $command
        }
    }
}

Invoke-SaveCommandCheck

try {
    $resolved = Resolve-IadskBinary -ExplicitPath $Binary
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}

Invoke-OverwriteCheck -ResolvedBinary $resolved

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
            Write-Output "Could not format iaDSK output."
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
