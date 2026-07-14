# Typography and Layout Standards

When building the JSON plan (Phase 3, Step 5), follow these typography and layout rules to ensure consistent, readable output.

## Typography Hierarchy

All text boxes in the JSON plan **must** specify `fontSize` explicitly. Never rely on the script default (11pt).

| Role | fontSize (pt) | bold | textColor | align | fontFamily |
|---|---|---|---|---|---|
| Main title | 18-20 | true | `RGB(0,51,102)` | 1 (center) | `Microsoft YaHei` |
| Section header | 13-16 | true | `RGB(40,40,40)` | 1 (center) | `Microsoft YaHei` |
| Box label | 10-12 | false | `RGB(50,50,50)` | 1 (center) | `Microsoft YaHei` |
| Small annotation | 8-10 | false | `RGB(100,100,100)` | 0 (left) | `Calibri` |
| Arrow / flow label | 9-11 | false | `RGB(60,60,60)` | 1 (center) | `Calibri` |
| Code / model names | 10-12 | false | `RGB(30,30,30)` | 1 (center) | `Consolas` |

### Font Family Guide

- Chinese text: `"Microsoft YaHei"` or `"SimHei"`
- English text: `"Calibri"` or `"Segoe UI"`
- Code / model names: `"Consolas"`

### Chinese Text Tips

- If a label wraps ugly, shorten the text, enlarge the box, or reduce fontSize slightly.
- Do not force long Chinese text into narrow boxes.
- Prefer Chinese punctuation over English punctuation in labels.
- Avoid mixing English abbreviations in Chinese labels unless necessary.

## Layout Standards

All measurements in pixels at the default 100 px = 1 inch scale.

| Element | Recommended Size |
|---|---|
| Canvas margin | 30-50 px on all sides |
| Gap between sibling boxes | 15-20 px |
| Gap between sections | 40-60 px |
| Main container box height | 80-100 px |
| Sub-container box height | 55-70 px |
| Small badge / icon area | 60-80 x 60-80 px |
| Arrow / connector width | 1.0-1.5 pt |
| Text box padding | implicit 6% via `TxtWidth = Width*0.94` |

### Layout Rules

- Boxes in the same row or section must have **identical heights** for visual consistency.
- Sidebar boxes need 15-20 px gaps (not 2-10 px).
- Total diagram height should be between 800-1500 px for typical route diagrams.
- Always leave margin on all sides; do not let shapes touch page edges.
- Draw large containers first, then details inside.
- Use coordinate-based duplication for repeated modules — do not eyeball each one.

## Title Placement Pattern

When a box has both a title and content text, **do not** put the title in the rectangle's `text` attribute (Visio centers it). Instead:

1. Create the rectangle with no `text` attribute.
2. Add a separate `text` type shape for the title, positioned near the top of the box (y1 + 8 to y1 + 25).
3. Add content `text` shapes below the title (y1 + 30+).

This avoids the centered-title-overlapping-content problem.
