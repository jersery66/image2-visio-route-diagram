---
name: image2-visio-route-diagram
description: Use when creating or repairing a Microsoft Visio technical route diagram, workflow figure, arXiv-style schematic, or grant-route figure that needs image2-generated icon modules with editable Visio text. Combines icon generation with Visio COM automation for deterministic, stable output.
---

# Image2 Visio Route Diagram

## Core Principle

Final Visio files must be **modular and deterministic**: image2-generated no-text transparent icon modules plus editable Visio text boxes and native Visio frames/arrows, assembled by a PowerShell COM automation script from a JSON plan. Never disguise a whole rendered picture as an editable Visio diagram. Never re-generate or overwrite the main `.vsdx` during validation.

## Required Workflow

### Phase 1: Analyze and Plan

1. **Analyze the reference image** — derive diagram outline, layout regions, bounding boxes, labels, color scheme, and canvas aspect ratio. Record pixel dimensions.

2. **Generate icon manifest** — create `icon_manifest.json` listing every icon module: `icon_id`, `meaning`, `prompt`, `key_color`, `file`, `placement`, `status`.

### Phase 2: Generate Icons

3. **Generate icon assets with image2** as separate no-text modules or a sprite sheet:
   - No Chinese or English text, no labels, letters, numbers, legends, titles, or watermarks.
   - Flat chroma-key background with generous padding and no clipping.
   - Blue/purple/orange modules: `#00ff00` is usually safe.
   - Green modules: use `#ff00ff`, **never** green chroma.
   - Mixed palettes: split into multiple sprite sheets by dominant color.

4. **Process icons** — remove chroma-key background, crop into individual transparent PNGs. Save each to a known path. See [Icon Asset Policy](#icon-asset-policy) and [Failure Recovery](#failure-recovery) below.

### Phase 3: Build Visio File

5. **Build JSON plan** — create a complete JSON plan (see `references/plan_schema_and_qa.md`) specifying:
   - Page dimensions matching the reference aspect ratio.
   - All native Visio shapes (containers, frames, arrows, connectors, ovals).
   - All image placements referencing the icon PNGs from Phase 2.
   - All text boxes with explicit `fontSize`, `textColor`, `bold`, and `fontFamily` following the typography standards below.

6. **Run the generation script** — execute `scripts/create_visio_from_plan.ps1` to produce the `.vsdx`:
   ```powershell
   powershell -File path/to/scripts/create_visio_from_plan.ps1 -PlanPath plan.json -OutVsdx output.vsdx -OutPng preview.png -BackupExisting
   ```
   Use `-BackupExisting` whenever the output path already has a file.

### Phase 4: Validate and Deliver

7. **Export PNG preview** — use `-OutPng` parameter, or export separately. Compare visually against the reference. If issues found, adjust the JSON plan and re-run (the script with `-BackupExisting` preserves the previous version).

8. **Inspect VSDX structure** — run `scripts/inspect_vsdx_structure.py` on the output. This is **read-only** and does not modify the `.vsdx`.

9. **Deliver** — provide `.vsdx` + PNG preview + `icon_manifest.json` + validation output.

## Critical Rule: No Overwrite During Validation

- The main `.vsdx` is written **exactly once** by `create_visio_from_plan.ps1`.
- If the output file already exists, use `-BackupExisting` to create a timestamped backup before overwriting.
- **Never** re-run the script during validation as a "check" — use `inspect_vsdx_structure.py` (read-only).
- **Never** embed the reference image as a page in the main `.vsdx` — this causes the diagram to look like a non-editable screenshot and was the root cause of the overwrite bug.
- If the user wants a side-by-side reference, save it as a **separate** `.vsdx` file.
- If validation fails, fix the JSON plan and re-run the script with `-BackupExisting`, never manually patch the `.vsdx`.

## Environment

Before starting, verify Visio and tools are available:

```powershell
powershell -File path/to/scripts/check_visio_environment.ps1 -TryCom
```

Requirements: Visio COM automation, Python for validation, optionally LibreOffice / pdftoppm for PNG fallback.

## Visio Plan Schema

Read `references/plan_schema_and_qa.md` for the complete JSON schema. Summary of shape types:

- `rect`: rectangle with optional text, fill, line, dash, roundX.
- `text`: text box (no fill, no line).
- `oval`: ellipse with bounding box coordinates.
- `line`: straight line with optional arrow.
- `polyline`: multi-segment line, arrow only on last segment.
- `image`: place a transparent PNG icon at center coordinates `(x, y)` with optional `widthPx` / `heightPx`.

Coordinate system: pixel-based, origin at top-left, x right, y down. Default scale: 100 px = 1 inch.

## Typography Standards

All text boxes in the JSON plan **must** specify `fontSize` explicitly. Never rely on the script default. Follow this hierarchy:

| Role | fontSize (pt) | bold | textColor | align | fontFamily |
|---|---|---|---|---|---|
| Main title | 18-20 | true | `RGB(0,51,102)` | 1 (center) | `Microsoft YaHei` |
| Section header | 13-16 | true | `RGB(40,40,40)` | 1 (center) | `Microsoft YaHei` |
| Box label | 10-12 | false | `RGB(50,50,50)` | 1 (center) | `Microsoft YaHei` |
| Small annotation | 8-10 | false | `RGB(100,100,100)` | 0 (left) | `Calibri` |
| Arrow / flow label | 9-11 | false | `RGB(60,60,60)` | 1 (center) | `Calibri` |
| Code / model names | 10-12 | false | `RGB(30,30,30)` | 1 (center) | `Consolas` |

**Chinese text tips**: if a label wraps ugly, shorten the text, enlarge the box, or reduce fontSize slightly. Do not force long Chinese text into narrow boxes. Use `"Microsoft YaHei"` or `"SimHei"` for all Chinese labels.

## Layout Standards

| Element | Recommended (px at 100 scale) |
|---|---|
| Canvas margin | 30-50 px all sides |
| Gap between sibling boxes | 15-20 px |
| Gap between sections | 40-60 px |
| Main container height | 80-100 px |
| Sub-container height | 55-70 px |
| Icon area | 60-80 x 60-80 px |

- Boxes in the same row or section must have **identical heights**.
- Sidebar boxes need 15-20 px gaps (not 2-10 px).
- Total diagram height should be between 800-1500 px for typical route diagrams.
- Always leave margin on all sides; do not let shapes touch page edges.

## Icon Asset Policy

Use one of these strategies, by preference:

1. **Preferred: generate each icon individually** — highest semantic accuracy.
2. **Allowed: sprite sheet + crop** — when icons share style and palette. Crop only from a dedicated sprite sheet, never from a full route diagram.
3. **Fallback: cropped references** — only for semantic understanding. Always regenerate clean icons from prompts.

### Quality requirements

| Requirement | Detail |
|---|---|
| Format | Separate transparent PNG per icon. |
| No text | No letters, numbers, labels, legends, watermarks in icons. |
| Consistent style | Same stroke weight, padding, perspective, color palette. |
| Minimum resolution | 512x512 px per icon; 1024x1024 for complex icons. |
| Green modules | Always use magenta `#ff00ff` chroma key. |

### Icon manifest fields

| Field | Purpose |
|---|---|
| `icon_id` | Unique identifier. |
| `meaning` | What the icon expresses. |
| `prompt` | The image2 prompt used. |
| `key_color` | Chroma-key color (e.g. `#00ff00`). |
| `file` | Final transparent-PNG filename. |
| `placement` | Which Visio module/region it belongs to. |
| `status` | `ok` / `regenerate` / `reject`. |

### Prompt pattern

```text
Generate a clean sprite sheet of separate no-text icon modules for a scientific technical route diagram.
Style: arXiv / Nature Methods schematic icons, polished vector-like bitmap, crisp outlines, consistent stroke.
Background: perfectly flat solid <KEY_COLOR> chroma-key for background removal.
Constraints: no Chinese text, no English text, no letters, no numbers, no labels, no legend, no watermark.
Each module must have generous padding, no clipping, and no shadows or reflections touching the background.
Modules: <ordered list of icon modules>.
```

For green modules, set `<KEY_COLOR>` to `#ff00ff`.

## Failure Recovery

| Symptom | Action |
|---|---|
| Residual text in icon | Regenerate with stronger no-text prompt. Do not manually erase. |
| Green/magenta halo | Change chroma key and regenerate. Do not mask harder. |
| Too blurry or small | Regenerate at higher resolution. Do not upscale. |
| Inconsistent style | Merge into one sprite sheet and regenerate together. |
| Semantic mismatch | Fix the prompt and regenerate. |
| Clipping / missing padding | Regenerate with explicit padding constraints. |

**Core rule**: always regenerate defective icons. Post-processing creates inconsistency.

## Non-Negotiables From Prior Corrections

- Do not hand-draw or code-draw content icons — generate them with image2.
- Do not extract icons from a full generated route image.
- Do not put text inside icon images — all labels are Visio text boxes.
- Do not use green chroma for green icons.
- Do not embed reference image as a page in the main `.vsdx` — root cause of overwrite bug.
- Do not re-run `create_visio_from_plan.ps1` without `-BackupExisting` when output exists.
- Do not claim editability if the final Visio is one large image.
- If icons look dirty, gray, or haloed, regenerate — do not over-mask.

## PowerShell and Visio Notes

- Windows PowerShell 5.1 may misread UTF-8 scripts with Chinese characters. If writing PS1 files with Chinese, add UTF-8 BOM after writing:
  ```python
  python -c "p='script.ps1'; c=open(p,'rb').read(); open(p,'wb').write(b'\xef\xbb\xbf'+c.lstrip(b'\xef\xbb\xbf'))"
  ```
- Visio COM startup needs 4-second wait after `New-Object -ComObject Visio.Application`.
- Set `AlertResponse = 7` to suppress dialogs (non-fatal if it fails).
- If COM rejects with `RPC_E_CALL_REJECTED`, close blank Visio windows, wait 10s, retry.
- If PNG export hangs, export EMF first and convert with LibreOffice or `pdftoppm`.
- Font cells: bold is `Char.Style` (NOT `Char.Bold`), size is `Char.Size`, family is `Char.Font`.
- In PowerShell double-quoted strings, avoid inline `$()` — pre-compute values into variables first.

## Final Delivery

Every deliverable must include:

- **Editable `.vsdx`** — generated by script, native shapes + text boxes + placed icon PNGs.
- **PNG preview** — exported from the main page for visual review.
- **`icon_manifest.json`** — all icon modules documented.
- **Validation output** — JSON result from `inspect_vsdx_structure.py`.

## Validation Checklist

Before final response, verify:

- Preview PNG exists and shows the main route page.
- VSDX has the expected single main page (no embedded reference page).
- Image shape count matches the number of generated icon modules.
- Text node count is nonzero and includes all labels.
- No `Original_Image_Reference` marker in the VSDX.
- No single image occupies more than 35% of the page area.
- Native shape count indicates actual Visio objects (frames, arrows, containers).
- Font sizes follow the typography hierarchy (all text has explicit fontSize).
- Gaps between boxes are 15-20 px, not 2-5 px.
- Icon manifest is complete with status and placement.
- The final answer states the editability boundary: icons are raster PNGs; text, frames, and arrows are editable Visio objects.

## Useful Commands

Check environment:
```powershell
powershell -File path/to/scripts/check_visio_environment.ps1 -TryCom
```

Generate Visio from JSON plan:
```powershell
powershell -File path/to/scripts/create_visio_from_plan.ps1 -PlanPath plan.json -OutVsdx output.vsdx -OutPng preview.png -BackupExisting
```

Inspect VSDX structure:
```powershell
E:/Anaconda/python.exe path/to/scripts/inspect_vsdx_structure.py output.vsdx --expect-single-page --min-media 5 --min-text 10 --min-image-shapes 5 --min-native-shapes 10 --forbid-reference --forbid-large-background-image
```

Remove chroma key for transparency:
```powershell
python "$env:USERPROFILE\.codex\skills\.system\imagegen\scripts\remove_chroma_key.py" --input sprite.png --out sprite_alpha.png --key-color "#ff00ff" --soft-matte --transparent-threshold 45 --opaque-threshold 170 --despill --force
```
