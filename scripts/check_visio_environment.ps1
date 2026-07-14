param(
    [switch]$TryCom,
    [switch]$KeepVisioOpen
)

$ErrorActionPreference = "Stop"

function Find-VisioExe {
    $cmd = Get-Command visio -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }

    $roots = @("C:/Program Files", "C:/Program Files (x86)")
    foreach ($root in $roots) {
        if (-not (Test-Path -LiteralPath $root)) { continue }
        $hit = Get-ChildItem -LiteralPath $root -Recurse -Filter VISIO.EXE -ErrorAction SilentlyContinue |
            Select-Object -First 1 -ExpandProperty FullName
        if ($hit) { return $hit }
    }
    return $null
}

function Find-Tool($names) {
    foreach ($name in $names) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd) { return $cmd.Source }
    }
    return $null
}

$result = [ordered]@{
    visioExe = Find-VisioExe
    soffice = Find-Tool @("soffice", "libreoffice")
    pdftoppm = Find-Tool @("pdftoppm")
    comStartup = "未测试"
    activeVisio = @()
}

$result.activeVisio = @(Get-Process VISIO -ErrorAction SilentlyContinue | ForEach-Object {
    [ordered]@{
        id = $_.Id
        title = $_.MainWindowTitle
        responding = $_.Responding
        startTime = $_.StartTime
    }
})

if ($TryCom) {
    $visio = $null
    try {
        for ($i = 1; $i -le 6; $i++) {
            try {
                $visio = New-Object -ComObject Visio.Application
                Start-Sleep -Milliseconds 800
                $visio.Visible = $true
                $visio.AlertResponse = 7
                $result.comStartup = "成功"
                break
            } catch {
                if ($i -eq 6) { throw }
                Start-Sleep -Milliseconds (700 * $i)
            }
        }
    } catch {
        $result.comStartup = "失败：$($_.Exception.Message)"
    } finally {
        if ($visio -ne $null -and -not $KeepVisioOpen) {
            try { $visio.Quit() } catch { }
        }
    }
}

$result | ConvertTo-Json -Depth 5
