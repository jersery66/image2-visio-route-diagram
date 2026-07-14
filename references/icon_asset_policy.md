# Icon Asset Policy

When the workflow reaches Phase 2 (Generate Icons), read this reference for icon generation rules, quality standards, and failure recovery.

## Asset Strategies (by preference)

1. **Preferred: generate each icon individually** — highest semantic accuracy. Use for important or complex modules.
2. **Allowed: sprite sheet + crop** — when icons share style and palette. Crop only from a dedicated sprite sheet, never from a full route diagram.
3. **Fallback: cropped references** — only for semantic understanding. Always regenerate clean icons from prompts.

### Single-icon vs. sprite-sheet decision

| Generate individually when... | Use sprite sheet only when... |
|---|---|
| Icon is semantically important (central model, key dataset) | Icons are visually simple (single object, few details) |
| Icon contains multiple objects or fine details | All modules share the same style and color palette |
| Icon failed once in a sprite sheet (semantic drift) | Primary goal is style consistency over semantic precision |
| Icon needs a distinct perspective or composition | |

**If semantic accuracy conflicts with style consistency, prioritize semantic accuracy.**

## Quality Requirements

| Requirement | Detail |
|---|---|
| Format | Separate transparent PNG per icon. |
| No text | No letters, numbers, labels, legends, watermarks in icons. |
| Consistent style | Same stroke weight, padding, perspective, color palette. |
| Minimum resolution | 512x512 px per icon; 1024x1024 for complex icons. Never upscale a small PNG inside Visio. |
| Green modules | Always use magenta `#ff00ff` chroma key. Never use green background. |
| Defect handling | Blurry, dirty, haloed, or semantically wrong icons must be regenerated — not post-processed. |

## Icon Manifest

Before generating any icons, produce an `icon_manifest.json` documenting every module:

| Field | Purpose |
|---|---|
| `icon_id` | Unique identifier. |
| `meaning` | What the icon expresses in the diagram. |
| `prompt` | The image2 prompt used to generate it. |
| `key_color` | Chroma-key background color (e.g. `#00ff00`). |
| `file` | Final transparent-PNG filename. |
| `placement` | Which Visio module or layout region it belongs to. |
| `status` | `ok` / `regenerate` / `reject`. |

## Prompt Pattern

```text
Generate a clean sprite sheet of separate no-text icon modules for a scientific technical route diagram.
Style: arXiv / Nature Methods schematic icons, polished vector-like bitmap, crisp outlines, consistent stroke.
Background: perfectly flat solid <KEY_COLOR> chroma-key for background removal.
Constraints: no Chinese text, no English text, no letters, no numbers, no labels, no legend, no watermark.
Each module must have generous padding, no clipping, and no shadows or reflections touching the background.
Modules: <ordered list of icon modules>.
```

For green modules, set `<KEY_COLOR>` to `#ff00ff`.

## Chroma Key Selection

| Icon dominant color | Safe chroma key |
|---|---|
| Blue / purple / orange / red | `#00ff00` (green) |
| Green | `#ff00ff` (magenta) |
| Mixed palette | Split into multiple sprite sheets by dominant color |

## Failure Recovery

When an icon asset fails quality checks, **always regenerate** — never post-process.

| Symptom | Action |
|---|---|
| Residual text in icon | Regenerate with a stronger prompt forbidding text. Do not manually erase. |
| Green/magenta halo on edges | Change chroma key (pick a color absent from the icon subject) and regenerate. Do not mask harder. |
| Icon too blurry or small | Regenerate at a higher resolution with the same prompt. Do not upscale in post-processing. |
| Inconsistent style across icons | Merge all modules into one sprite sheet and regenerate together for visual consistency. |
| Semantic mismatch (wrong object) | Fix the prompt description and regenerate. Do not keep a wrong icon just because it looks clean. |
| Clipping or missing padding | Regenerate with explicit padding and `no clipping` constraints. Do not pad by stretching the canvas. |

## Chroma Key Removal Command

The repository includes a standalone chroma-key removal script:

```powershell
python scripts/remove_chroma_key.py --input sprite.png --out sprite_alpha.png --key-color "#ff00ff" --soft-matte --despill --force
```

Requires `Pillow` and `numpy` (`pip install Pillow numpy`).
