param(
    [Parameter(Mandatory = $true)]
    [string]$PlanPath,

    [Parameter(Mandatory = $true)]
    [string]$OutVsdx,

    [string]$OutEmf = "",
    [string]$OutPng = "",
    [switch]$Visible,
    [switch]$KeepVisioOpen,
    [switch]$BackupExisting
)

$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Safety: backup existing output file before overwriting
# ---------------------------------------------------------------------------
if ((Test-Path -LiteralPath $OutVsdx) -and $BackupExisting) {
    $ts = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupName = [System.IO.Path]::GetFileNameWithoutExtension($OutVsdx) + "_backup_$ts" + [System.IO.Path]::GetExtension($OutVsdx)
    $backupPath = Join-Path ([System.IO.Path]::GetDirectoryName($OutVsdx)) $backupName
    Copy-Item -LiteralPath $OutVsdx -Destination $backupPath
    Write-Host "Backed up existing file to: $backupPath"
}

# ---------------------------------------------------------------------------
# Load plan
# ---------------------------------------------------------------------------
if (-not (Test-Path -LiteralPath $PlanPath)) {
    throw "Plan file not found: $PlanPath"
}

$plan = Get-Content -LiteralPath $PlanPath -Raw -Encoding UTF8 | ConvertFrom-Json
$outDir = Split-Path -Parent $OutVsdx
if ($outDir) { New-Item -ItemType Directory -Force -Path $outDir | Out-Null }
if ($OutEmf -and (Split-Path -Parent $OutEmf)) {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $OutEmf) | Out-Null
}
if ($OutPng -and (Split-Path -Parent $OutPng)) {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $OutPng) | Out-Null
}

# ---------------------------------------------------------------------------
# Page globals
# ---------------------------------------------------------------------------
$script:page = $null
$script:pageHeightPx = [double]($plan.page.heightPx)
$script:scale = if ($plan.page.scalePxPerInch) { [double]$plan.page.scalePxPerInch } else { 100.0 }

function X([double]$px) { $px / $script:scale }
function Y([double]$py) { ($script:pageHeightPx - $py) / $script:scale }
function Cell($shape, [string]$cell, [string]$formula) {
    try { $shape.CellsU($cell).FormulaU = $formula } catch { }
}

# ---------------------------------------------------------------------------
# Styling helpers
# ---------------------------------------------------------------------------
function Style-Shape($shape, $style) {
    $fill    = if ($style.fill)    { $style.fill }    else { "RGB(255,255,255)" }
    $line    = if ($style.line)    { $style.line }    else { "RGB(35,35,35)" }
    $weight  = if ($style.weight)  { [double]$style.weight } else { 1.0 }
    $dash    = [bool]$style.dash
    $noFill  = [bool]$style.noFill
    $noLine  = [bool]$style.noLine
    $roundX  = if ($style.roundX)  { [double]$style.roundX } else { 0.0 }

    if ($noFill) {
        Cell $shape "FillPattern" "0"
    } else {
        Cell $shape "FillPattern" "1"
        Cell $shape "FillForegnd" $fill
    }
    if ($noLine) {
        Cell $shape "LinePattern" "0"
    } else {
        Cell $shape "LinePattern" $(if ($dash) { "2" } else { "1" })
        Cell $shape "LineColor" $line
        Cell $shape "LineWeight" "$weight pt"
    }
    # Rounded corners (value in inches; 0 = sharp corners)
    if ($roundX -gt 0) { Cell $shape "Rounding" "$roundX in" }
}

function Style-Text($shape, $style) {
    # Default 11pt (was 8pt in earlier versions) for better readability
    $font       = if ($style.fontSize)  { [double]$style.fontSize }  else { 11.0 }
    $color      = if ($style.textColor) { $style.textColor }         else { "RGB(40,40,40)" }
    $bold       = [bool]$style.bold
    $align      = if ($null -ne $style.align) { [int]$style.align }  else { 1 }
    $fontFamily = if ($style.fontFamily) { $style.fontFamily }       else { "" }

    Cell $shape "Char.Size"  "$font pt"
    Cell $shape "Char.Color" $color
    # IMPORTANT: bold cell is Char.Style (NOT Char.Bold or Character.Style)
    Cell $shape "Char.Style" $(if ($bold) { "1" } else { "0" })
    Cell $shape "Para.HorzAlign" "$align"
    Cell $shape "VerticalAlign"  "1"
    Cell $shape "TxtWidth"       "Width*0.94"

    # Font family - use exact installed font name
    if ($fontFamily -ne "") {
        Cell $shape "Char.Font" $fontFamily
    }
}

# ---------------------------------------------------------------------------
# Shape drawing dispatcher
# ---------------------------------------------------------------------------
function Draw-Shape($item) {
    $type  = "$($item.type)".ToLowerInvariant()
    $style = if ($item.style) { $item.style } else { [pscustomobject]@{} }
    $text  = if ($null -ne $item.text) { [string]$item.text } else { "" }

    # --- Rectangle or text box ---
    if ($type -eq "rect" -or $type -eq "text") {
        $shape = $script:page.DrawRectangle((X $item.x1), (Y $item.y2), (X $item.x2), (Y $item.y1))
        if ($type -eq "text") {
            $style | Add-Member -NotePropertyName noFill -NotePropertyValue $true -Force
            $style | Add-Member -NotePropertyName noLine -NotePropertyValue $true -Force
        }
        Style-Shape $shape $style
        if ($text -ne "") { $shape.Text = $text; Style-Text $shape $style }
        return
    }

    # --- Oval ---
    if ($type -eq "oval") {
        $shape = $script:page.DrawOval((X $item.x1), (Y $item.y2), (X $item.x2), (Y $item.y1))
        Style-Shape $shape $style
        if ($text -ne "") { $shape.Text = $text; Style-Text $shape $style }
        return
    }

    # --- Straight line ---
    if ($type -eq "line") {
        $shape = $script:page.DrawLine((X $item.x1), (Y $item.y1), (X $item.x2), (Y $item.y2))
        $style | Add-Member -NotePropertyName noFill -NotePropertyValue $true -Force
        Style-Shape $shape $style
        Set-Arrow $shape $item.arrow
        return
    }

    # --- Polyline (multi-segment) ---
    if ($type -eq "polyline") {
        $points = @($item.points)
        for ($i = 0; $i -lt ($points.Count - 1); $i++) {
            $p1 = $points[$i]
            $p2 = $points[$i + 1]
            $shape = $script:page.DrawLine((X $p1[0]), (Y $p1[1]), (X $p2[0]), (Y $p2[1]))
            $style | Add-Member -NotePropertyName noFill -NotePropertyValue $true -Force
            Style-Shape $shape $style
            if ($i -eq ($points.Count - 2)) { Set-Arrow $shape $item.arrow }
        }
        return
    }

    # --- Image (place transparent PNG icon on the page) ---
    if ($type -eq "image") {
        $filePath = [string]$item.filePath
        if (-not (Test-Path -LiteralPath $filePath)) {
            Write-Warning "Image file not found, skipping: $filePath"
            return
        }
        $pic = $script:page.Import($filePath)
        # Position by center point
        if ($item.x -and $item.y) {
            $pic.CellsU("PinX").FormulaU = "$(X $item.x) in"
            $pic.CellsU("PinY").FormulaU = "$(Y $item.y) in"
        }
        # Set display size; aspect ratio is locked
        if ($item.widthPx) {
            $pic.CellsU("Width").FormulaU = "$(X $item.widthPx) in"
        }
        if ($item.heightPx) {
            $pic.CellsU("Height").FormulaU = "$(X $item.heightPx) in"
        }
        $pic.CellsU("LockAspect").FormulaU = "1"
        return
    }

    throw "Unsupported shape type: $type"
}

# ---------------------------------------------------------------------------
# Arrow helper
# ---------------------------------------------------------------------------
function Set-Arrow($shape, $arrow) {
    $value = if ($arrow) { "$arrow" } else { "end" }
    if ($value -eq "end"  -or $value -eq "both") { Cell $shape "EndArrow"   "13" }
    if ($value -eq "begin" -or $value -eq "both") { Cell $shape "BeginArrow" "13" }
}

# ---------------------------------------------------------------------------
# COM robustness helpers
# ---------------------------------------------------------------------------
function Invoke-ComRetry([scriptblock]$Action, [int]$Attempts = 10, [int]$BaseDelayMs = 500) {
    for ($i = 1; $i -le $Attempts; $i++) {
        try { return & $Action } catch {
            if ($i -eq $Attempts) { throw }
            Start-Sleep -Milliseconds ($BaseDelayMs * $i)
        }
    }
}

function New-VisioApplication {
    for ($i = 1; $i -le 5; $i++) {
        $app = $null
        try {
            $app = New-Object -ComObject Visio.Application
            Start-Sleep -Seconds 4
            return $app
        } catch {
            if ($app -ne $null) { try { $app.Quit() } catch { } }
            if ($i -eq 5) {
                throw "Cannot start Visio via COM. Close any blank Visio windows, wait a few seconds, and retry. Error: $($_.Exception.Message)"
            }
            Start-Sleep -Seconds (2 * $i)
        }
    }
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
$script:visio = $null
$doc = $null
try {
    $script:visio = New-VisioApplication
    if ($Visible) { Invoke-ComRetry { $script:visio.Visible = $true } | Out-Null }
    try { Invoke-ComRetry { $script:visio.AlertResponse = 7 } | Out-Null } catch { }

    $doc = Invoke-ComRetry { $script:visio.Documents.Add("") }

    $script:page = $script:visio.ActivePage
    $script:page.Name = if ($plan.page.name) { [string]$plan.page.name } else { "Visio Diagram" }
    $script:page.PageSheet.CellsU("PageWidth").FormulaU  = "$([double]$plan.page.widthPx  / $script:scale) in"
    $script:page.PageSheet.CellsU("PageHeight").FormulaU = "$([double]$plan.page.heightPx / $script:scale) in"

    # Draw all shapes from the plan
    foreach ($shape in @($plan.shapes)) {
        Draw-Shape $shape
    }

    # NOTE: Reference image is intentionally NOT embedded in the main .vsdx.
    # The reference stays external to prevent:
    #   1) The output looking like a non-editable pasted screenshot
    #   2) The validation-step overwrite bug where re-running the script
    #      with a reference page replaces the user's working diagram

    # Save
    $doc.SaveAs($OutVsdx)

    # Export EMF (if requested)
    if ($OutEmf) {
        Invoke-ComRetry { $script:page.Export($OutEmf) } | Out-Null
    }

    # Export PNG (if requested) - direct first, fallback warning
    if ($OutPng) {
        $pngOk = $false
        try {
            Invoke-ComRetry { $script:page.Export($OutPng) } | Out-Null
            $pngOk = $true
        } catch {
            Write-Warning "Direct PNG export failed."
        }
        if (-not $pngOk -and $OutEmf -and (Test-Path -LiteralPath $OutEmf)) {
            Write-Warning "Use the EMF file and convert with LibreOffice or pdftoppm."
        } elseif (-not $pngOk) {
            Write-Warning "PNG export failed. Try exporting manually from Visio."
        }
    }

    # Output summary as JSON
    [pscustomobject]@{
        vsdx     = $OutVsdx
        emf      = $OutEmf
        png      = $OutPng
        pages    = $doc.Pages.Count
        shapes   = @($plan.shapes).Count
    } | ConvertTo-Json -Depth 3
}
finally {
    if ($doc -ne $null) { try { $doc.Saved = $true } catch { } }
    if ($script:visio -ne $null -and -not $KeepVisioOpen) {
        try { $script:visio.Quit() } catch { }
    }
}
