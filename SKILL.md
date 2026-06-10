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

## Icon Asset Policy

Use one of the following icon-asset strategies, listed by preference:

### 1. Preferred: generate each icon module directly

For important or complex modules, generate one no-text icon at a time on a flat chroma-key background. This gives the highest semantic accuracy and avoids layout contamination from a full route diagram.

### 2. Allowed: generate a sprite sheet and crop modules

A sprite sheet may be used when multiple icons share the same style and color palette. After generation, remove the chroma-key background and crop each module into an individual transparent PNG. **Cropping is allowed only from a dedicated icon sprite sheet, not from a full rendered route diagram.**

### 3. Fallback: use cropped reference icons only as semantic references

If the user provides a low-resolution route diagram or screenshot, cropped icons may be used only to understand the intended meaning and style. Do not upscale and reuse them as final assets. Instead, regenerate clean no-text icon modules from prompts derived from those references.

### Quality requirements (all strategies)

| Requirement | Detail |
|---|---|
| Format | Each final icon must be a separate transparent PNG. |
| No text | No Chinese text, English text, letters, numbers, labels, legends, or watermarks inside icon images. |
| Consistent style | Icons must share consistent visual style, stroke weight, padding, perspective, and color palette. |
| Minimum resolution | Each cropped icon must be at least **512×512 px**; complex icons should be **1024×1024 px**. Never forcibly upscale a small PNG inside Visio. |
| Defect handling | If an icon is blurry, dirty, haloed, clipped, or semantically wrong after background removal, regenerate the module — do not over-mask or upscale it. |
| Green modules | Always use magenta `#ff00ff` chroma key for green icons. Never use a green background. |

### Icon manifest

Before generating any icons, produce an `icon_manifest.json` (or equivalent table) documenting every module:

| Field | Purpose |
|---|---|
| `icon_id` | Unique identifier for this icon. |
| `meaning` | What the icon expresses in the diagram. |
| `prompt` | The image2 prompt used to generate it. |
| `key_color` | Chroma-key background color (e.g. `#00ff00`). |
| `file` | Final transparent-PNG filename. |
| `placement` | Which Visio module or layout region it belongs to. |
| `status` | One of: `ok` / `regenerate` / `reject`. |

The manifest helps the agent plan consistently and lets you review or re-generate individual icons without touching unrelated modules.

## Failure Recovery

When an icon asset fails quality checks, follow these rules instead of trying to repair the image:

| Symptom | Action |
|---|---|
| Residual text in icon | Regenerate with a stronger prompt forbidding text. Do not manually erase. |
| Green/magenta halo on edges | Change chroma key (pick a color absent from the icon subject) and regenerate. Do not mask harder. |
| Icon too blurry or small | Regenerate at a higher resolution with the same prompt. Do not upscale in post-processing. |
| Inconsistent style across icons | Merge all modules into one sprite sheet and regenerate together for visual consistency. |
| Semantic mismatch (wrong object) | Fix the prompt description and regenerate. Do not keep a wrong icon just because it looks clean. |
| Clipping or missing padding | Regenerate with explicit padding and `no clipping` constraints. Do not pad by stretching the image canvas. |

**Core rule**: when an icon is defective, always regenerate it. Post-processing tricks (eraser, clone stamp, forced upscale, alpha tweaks) create inconsistency and waste time. The only exception is chroma-key removal, which is a deterministic local operation.

## Validation Checklist

Before final response, verify:

- Preview PNG exists and shows the main route page.
- VSDX has the expected single main page unless user asked for references.
- Media count roughly equals the number of generated icon modules, not `1`.
- Text node count is nonzero and includes the labels/descriptions.
- No `Original_Image_Reference` marker is present in the final VSDX.
- No single image occupies more than 35 % of the page area (run `--forbid-large-background-image`).
- Icon manifest (or equivalent) is complete with status and placement.
- The final answer states the editability boundary: icon modules are raster PNGs; text boxes, frames, and arrows are editable Visio objects.

## Useful Commands

Inspect a VSDX with all checks:

```powershell
python path\to\scripts\inspect_vsdx_structure.py output.vsdx --expect-single-page --min-media 5 --min-text 10 --forbid-reference --forbid-large-background-image
```

Check for unexpectedly large background images only:

```powershell
python path\to\scripts\inspect_vsdx_structure.py output.vsdx --forbid-large-background-image --max-image-area-ratio 0.35
```

Use the imagegen skill's chroma-key helper for transparency:

```powershell
python "$env:USERPROFILE\.codex\skills\.system\imagegen\scripts\remove_chroma_key.py" --input sprite.png --out sprite_alpha.png --key-color "#ff00ff" --soft-matte --transparent-threshold 45 --opaque-threshold 170 --despill --force
```

