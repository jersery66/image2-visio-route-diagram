---
name: image2-visio-route-diagram
description: Use when creating or repairing a Microsoft Visio technical route diagram, workflow figure, arXiv-style schematic, or grant-route figure that needs image2-generated icon modules with editable Visio text.
---

# Image2 Visio Route Diagram

## Core Principle

Final Visio files must be modular: image2-generated no-text transparent icon modules plus editable Visio text boxes and native Visio frames/arrows. Never disguise a whole rendered picture as an editable Visio diagram.

## Required Workflow

1. Derive the diagram outline and layout from the proposal/reference figure.
2. Generate a full draft image only for visual direction if helpful. Do not use that full image as the final Visio content.
3. Generate icon assets with image2/image_gen as separate no-text modules or a sprite sheet. Prompt for:
   - no Chinese or English text
   - no labels, letters, numbers, legends, titles, or watermarks
   - flat chroma-key background
   - generous padding and no clipping
4. Choose chroma key by icon color, then remove locally:
   - Blue/purple/orange modules: `#00ff00` is usually safe.
   - Green modules: use `#ff00ff`, not green.
   - Mixed palettes: split into multiple image2 sprite sheets by dominant color.
5. Crop from the image2 sprite sheet into individual transparent PNG modules. Do not crop icons from a full route-diagram screenshot.
6. Build the Visio page from:
   - transparent PNG modules positioned by layout coordinates
   - native Visio rectangles/roundrects/lines/arrows for frames and connectors when possible
   - editable Visio text boxes for all explanatory text
7. Do not include a final reference page or background image unless explicitly requested. If a reference page was useful while building, remove it or save the main page active.
8. Export a PNG preview and compare it visually before claiming completion.
9. Inspect the VSDX package before delivery. Use `scripts/inspect_vsdx_structure.py` from this skill or an equivalent check.

## Non-Negotiables From Prior Corrections

- Do not hand-draw or code-draw content icons when the user asked for image2-generated icons. Native Visio shapes are fine for frames, arrows, badges, and simple containers.
- Do not extract icons from the whole generated route image; generate/re-generate each module or module sprite sheet directly.
- Do not put text inside icon images. All labels such as `LLM`, `HAMD-17`, `PHQ-9`, `MAE`, `AUC`, dataset names, and Chinese descriptions must be Visio text boxes.
- Do not use green chroma key for green icon modules. Regenerate green rows/modules on magenta `#ff00ff`.
- Do not claim editability if the final Visio is one large image. Verify text nodes and module counts.
- Do not leave an `Original_Image_Reference` page as the page Visio opens to; this makes the file look like a single non-editable picture.
- If a row looks dirty, gray, eaten, or haloed after background removal, regenerate that row/module with a safer key color instead of masking harder.

## Prompt Pattern

Use this pattern for module generation:

```text
Generate a clean sprite sheet of separate no-text icon modules for a scientific technical route diagram.
Style: arXiv / Nature Methods schematic icons, polished vector-like bitmap, crisp outlines, consistent stroke.
Background: perfectly flat solid <KEY_COLOR> chroma-key for background removal.
Constraints: no Chinese text, no English text, no letters, no numbers, no labels, no legend, no watermark.
Each module must have generous padding, no clipping, and no shadows or reflections touching the background.
Modules: <ordered list of icon modules>.
```

For green modules, set `<KEY_COLOR>` to `#ff00ff`.

## Validation Checklist

Before final response, verify:

- Preview PNG exists and shows the main route page.
- VSDX has the expected single main page unless user asked for references.
- Media count roughly equals the number of generated icon modules, not `1`.
- Text node count is nonzero and includes the labels/descriptions.
- No `Original_Image_Reference` marker is present in the final VSDX.
- The final answer states the editability boundary: icon modules are raster PNGs; text boxes, frames, and arrows are editable Visio objects.

## Useful Commands

Inspect a VSDX:

```powershell
python path\to\scripts\inspect_vsdx_structure.py output.vsdx --expect-single-page --min-media 5 --min-text 10 --forbid-reference
```

Use the imagegen skill's chroma-key helper for transparency:

```powershell
python "$env:USERPROFILE\.codex\skills\.system\imagegen\scripts\remove_chroma_key.py" --input sprite.png --out sprite_alpha.png --key-color "#ff00ff" --soft-matte --transparent-threshold 45 --opaque-threshold 170 --despill --force
```

