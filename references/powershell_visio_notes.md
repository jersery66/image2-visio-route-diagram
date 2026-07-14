# PowerShell and Visio COM Notes

Technical notes for working with Visio COM automation. Read when writing or debugging PowerShell scripts.

## Environment Check

Before starting any Visio automation, verify the environment:

```powershell
powershell -File path/to/scripts/check_visio_environment.ps1 -TryCom
```

This checks for Visio executable, COM startup, LibreOffice, and pdftoppm availability.

## UTF-8 BOM Requirement

Windows PowerShell 5.1 may misread UTF-8 scripts containing Chinese characters. If writing `.ps1` files with Chinese text, add UTF-8 BOM after writing:

```python
python -c "p='script.ps1'; c=open(p,'rb').read(); open(p,'wb').write(b'\xef\xbb\xbf'+c.lstrip(b'\xef\xbb\xbf'))"
```

The `create_visio_from_plan.ps1` script itself is ASCII-only (no Chinese in code), so it does not need BOM. But any custom PS1 scripts with Chinese labels do.

## Visio COM Startup

- Visio needs a **4-second wait** after `New-Object -ComObject Visio.Application` before making COM calls.
- Set `AlertResponse = 7` to suppress auto-save dialogs (non-fatal if it fails).
- The script includes retry logic (5 attempts with increasing delay) for COM startup.

## Path Format

**Visio COM SaveAs/Export paths MUST use backslashes** (`C:\path\file`), not forward slashes. Forward slashes cause `COMException` with "未知异常" error message.

When calling the script from bash, pass paths with backslashes:
```powershell
powershell -File script.ps1 -OutVsdx "C:\Users\name\output.vsdx"
```

## Common COM Issues

| Symptom | Fix |
|---|---|
| `RPC_E_CALL_REJECTED` | Close all blank Visio windows, wait 10s, retry |
| PNG export hangs or fails | Export EMF first, then convert with LibreOffice or `pdftoppm` |
| SaveAs fails with COMException | Check path uses backslashes; ensure directory exists |
| Chinese text garbled in PS1 | Add UTF-8 BOM to the script file |

## Visio Cell Reference

| Property | Cell Name | Notes |
|---|---|---|
| Bold | `Char.Style` | NOT `Char.Bold` or `Character.Style` |
| Font size | `Char.Size` | Formula: `"11 pt"` |
| Font family | `Char.Font` | Use exact installed font name |
| Text color | `Char.Color` | Formula: `"RGB(40,40,40)"` |
| Horizontal align | `Para.HorzAlign` | 0=left, 1=center, 2=right |
| Vertical align | `VerticalAlign` | 1=center |
| Text width | `TxtWidth` | Formula: `"Width*0.94"` for 6% padding |
| Fill color | `FillForegnd` | Formula: `"RGB(255,255,255)"` |
| Fill pattern | `FillPattern` | 0=none, 1=solid |
| Line color | `LineColor` | Formula: `"RGB(35,35,35)"` |
| Line weight | `LineWeight` | Formula: `"1.0 pt"` |
| Line pattern | `LinePattern` | 0=none, 1=solid, 2=dashed |
| Corner rounding | `Rounding` | Formula: `"0.1 in"` (0 = sharp) |
| Arrow style | `EndArrow` / `BeginArrow` | 13 = standard arrow |

## PowerShell String Quoting

In PowerShell double-quoted strings, avoid inline `$()` expressions — the Visio CellsU formula parser may break. Pre-compute values into variables first:

```powershell
# BAD: formula contains $() inside double-quoted string
$shape.CellsU("PinX").FormulaU = "$($px / $scale) in"

# GOOD: pre-compute into variable
$pinX = $px / $scale
$shape.CellsU("PinX").FormulaU = "$pinX in"
```

## Useful Commands

### Generate Visio from JSON plan
```powershell
powershell -File path/to/scripts/create_visio_from_plan.ps1 -PlanPath plan.json -OutVsdx output.vsdx -OutPng preview.png -BackupExisting
```

### Inspect VSDX structure (read-only validation)
```powershell
E:/Anaconda/python.exe path/to/scripts/inspect_vsdx_structure.py output.vsdx --expect-single-page --min-media 5 --min-text 10 --min-image-shapes 5 --min-native-shapes 10 --forbid-reference --forbid-large-background-image
```

### PNG export fallback via LibreOffice
```powershell
& "C:\Users\Jersery\AppData\Local\Programs\LibreOffice-26.2.4\program\soffice.com" --headless --convert-to pdf output.vsdx
pdftoppm -png -r 150 output.pdf preview
```
