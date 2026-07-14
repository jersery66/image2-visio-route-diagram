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
2. **Generate icon manifest** — create `icon_manifest.json` listing every icon module. See [Icon Asset Policy](references/icon_asset_policy.md) for manifest fields and generation strategies.

### Phase 2: Generate Icons

3. **Generate icon assets with image2** as separate no-text modules or a sprite sheet. Follow [Icon Asset Policy](references/icon_asset_policy.md) for chroma key selection, quality requirements, and prompt patterns.
4. **Process icons** — remove chroma-key background, crop into individual transparent PNGs. Save each to a known absolute path for the JSON plan.

### Phase 3: Build Visio File

5. **Build JSON plan** — create a complete JSON plan following [Plan Schema](references/plan_schema_and_qa.md) and [Typography & Layout](references/typography_and_layout.md):
   - Page dimensions matching the reference aspect ratio.
   - All native Visio shapes (containers, frames, arrows, connectors, ovals).
   - All `image` placements referencing the icon PNG absolute paths from Phase 2.
   - All text boxes with explicit `fontSize`, `textColor`, `bold`, and `fontFamily`.
6. **Run the generation script**:
   ```powershell
   powershell -File path/to/scripts/create_visio_from_plan.ps1 -PlanPath plan.json -OutVsdx output.vsdx -OutPng preview.png -BackupExisting
   ```
   Always use `-BackupExisting` when the output path already has a file.

### Phase 4: Validate and Deliver

7. **Export PNG preview** — compare visually against the reference. If issues found, adjust the JSON plan and re-run with `-BackupExisting`.
8. **Inspect VSDX structure** — run `scripts/inspect_vsdx_structure.py` (read-only, does not modify the `.vsdx`).
9. **Deliver** — provide all four artifacts listed in [Final Delivery](#final-delivery).

## Critical Rule: No Overwrite During Validation

- The main `.vsdx` is written **exactly once** by `create_visio_from_plan.ps1`.
- If the output file already exists, use `-BackupExisting` to create a timestamped backup.
- **Never** re-run the script during validation — use `inspect_vsdx_structure.py` (read-only).
- **Never** embed the reference image as a page in the main `.vsdx`.
- If the user wants a side-by-side reference, save it as a **separate** `.vsdx` file.
- If validation fails, fix the JSON plan and re-run with `-BackupExisting`.

## Non-Negotiables

- Do not hand-draw content icons — generate them with image2.
- Do not extract icons from a full generated route image.
- Do not put text inside icon images — all labels are Visio text boxes.
- Do not use green chroma for green icons (use magenta `#ff00ff`).
- Do not embed reference image in the main `.vsdx`.
- Do not re-run the generation script without `-BackupExisting` when output exists.
- Do not claim editability if the final Visio is one large image.
- Defective icons: always regenerate, never post-process.

## Final Delivery

Every deliverable must include:

- **Editable `.vsdx`** — native shapes + text boxes + placed icon PNGs.
- **PNG preview** — rendered export of the main page.
- **`icon_manifest.json`** — all icon modules documented.
- **Validation output** — JSON result from `inspect_vsdx_structure.py`.

## Validation Checklist

- Preview PNG exists and shows the main route page.
- VSDX has the expected single main page (no embedded reference page).
- Image shape count matches generated icon modules; native shape count > 0.
- Text node count is nonzero and includes all labels.
- No `Original_Image_Reference` marker in the VSDX.
- No single image occupies more than 35% of the page area.
- Font sizes follow the typography hierarchy; gaps between boxes are 15-20 px.
- Icon manifest is complete with status and placement.
- Final answer states the editability boundary: icons are raster PNGs; text, frames, and arrows are editable Visio objects.

## Reference Documents

| Document | When to Read |
|---|---|
| [Plan Schema & QA](references/plan_schema_and_qa.md) | Phase 3, Step 5 — building the JSON plan |
| [Typography & Layout](references/typography_and_layout.md) | Phase 3, Step 5 — font sizes, spacing, title placement |
| [Icon Asset Policy](references/icon_asset_policy.md) | Phase 1-2 — icon generation, chroma key, failure recovery |
| [PowerShell & Visio Notes](references/powershell_visio_notes.md) | When writing/debugging PS1 scripts or troubleshooting COM |
| [Icon Manifest Template](references/icon_manifest_template.json) | Phase 1 — sample manifest structure |
| `scripts/visio_plan_builder.py` | Phase 3 — reusable layout primitives for plan generation |
| `scripts/remove_chroma_key.py` | Phase 2 — standalone chroma-key background removal |
| `tests/test_inspect.py` | Development — automated tests for the VSDX inspector |
