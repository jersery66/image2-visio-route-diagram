# Visio JSON Plan Schema and QA Checklist

When creating a JSON plan for `scripts/create_visio_from_plan.ps1`, read this reference file.

## Minimal Example

```json
{
  "page": {
    "name": "Technical Route Diagram",
    "widthPx": 1440,
    "heightPx": 1000,
    "scalePxPerInch": 100
  },
  "shapes": [
    {
      "type": "rect",
      "x1": 20,
      "y1": 90,
      "x2": 1420,
      "y2": 980,
      "text": "",
      "style": {
        "fill": "RGB(255,255,255)",
        "line": "RGB(88,103,150)",
        "weight": 1.4,
        "dash": true,
        "roundX": 0.1
      }
    },
    {
      "type": "text",
      "x1": 590,
      "y1": 35,
      "x2": 850,
      "y2": 75,
      "text": "Research Framework",
      "style": {
        "fontSize": 20,
        "textColor": "RGB(0,51,102)",
        "bold": true,
        "fontFamily": "Microsoft YaHei"
      }
    },
    {
      "type": "image",
      "filePath": "C:/path/to/icons/brain_icon.png",
      "x": 200,
      "y": 300,
      "widthPx": 80,
      "heightPx": 80
    },
    {
      "type": "line",
      "x1": 300,
      "y1": 200,
      "x2": 430,
      "y2": 200,
      "arrow": "end",
      "style": {
        "weight": 1.2
      }
    },
    {
      "type": "polyline",
      "points": [[300, 250], [300, 310], [430, 310]],
      "arrow": "end",
      "style": {
        "weight": 1.2
      }
    },
    {
      "type": "oval",
      "x1": 500,
      "y1": 220,
      "x2": 550,
      "y2": 270,
      "text": "API",
      "style": {
        "fill": "RGB(231,252,255)",
        "line": "RGB(35,188,211)",
        "fontSize": 10,
        "textColor": "RGB(34,139,155)"
      }
    }
  ]
}
```

## Page Fields

| Field | Required | Description |
|---|---|---|
| `name` | No | Page name shown in Visio tab. Default: `"Visio Diagram"`. |
| `widthPx` | Yes | Page width in pixels. |
| `heightPx` | Yes | Page height in pixels. |
| `scalePxPerInch` | No | Pixels per Visio inch. Default: `100`. |

## Shape Types

### `rect` — Rectangle

| Field | Required | Description |
|---|---|---|
| `x1`, `y1` | Yes | Top-left corner (px). |
| `x2`, `y2` | Yes | Bottom-right corner (px). |
| `text` | No | Label text inside the rectangle. |
| `style.fill` | No | Fill color formula, e.g. `"RGB(240,245,255)"`. Default: white. |
| `style.line` | No | Border color formula. Default: `"RGB(35,35,35)"`. |
| `style.weight` | No | Border width in pt. Default: `1.0`. |
| `style.dash` | No | `true` for dashed border. |
| `style.roundX` | No | Corner rounding radius in inches. Default: `0`. |
| `style.noFill` | No | `true` to remove fill. |
| `style.noLine` | No | `true` to remove border. |

### `text` — Text box

Same coordinates as `rect`, but automatically sets `noFill` and `noLine`. Used for labels, titles, and descriptions.

### `oval` — Ellipse

| Field | Required | Description |
|---|---|---|
| `x1`, `y1`, `x2`, `y2` | Yes | Bounding box of the ellipse. |
| `text` | No | Label text. |
| `style.*` | No | Same as `rect`. |

### `line` — Straight line

| Field | Required | Description |
|---|---|---|
| `x1`, `y1` | Yes | Start point (px). |
| `x2`, `y2` | Yes | End point (px). |
| `arrow` | No | `"none"`, `"begin"`, `"end"`, `"both"`. Default: `"end"`. |
| `style.weight` | No | Line width in pt. |

### `polyline` — Multi-segment line

| Field | Required | Description |
|---|---|---|
| `points` | Yes | Array of `[x, y]` pairs. Minimum 2 points. |
| `arrow` | No | Arrow only on the last segment. Same options as `line`. |
| `style.*` | No | Same as `line`. |

### `image` — Place PNG icon

| Field | Required | Description |
|---|---|---|
| `filePath` | Yes | Absolute path to the transparent PNG file. |
| `x` | Yes | Center X position (px). |
| `y` | Yes | Center Y position (px). |
| `widthPx` | No | Display width (px). Aspect ratio locked. |
| `heightPx` | No | Display height (px). Aspect ratio locked. |

If `widthPx` or `heightPx` is omitted, the image keeps its native size at the page scale.

## Coordinate System

- Origin: **top-left** of the page.
- X increases **rightward**, Y increases **downward**.
- Conversion: `inches = pixels / scalePxPerInch`.
- The script flips Y internally because Visio's origin is bottom-left.

## Typography Reference

Use these defaults unless the plan explicitly overrides them:

| Role | fontSize | bold | textColor | align |
|---|---|---|---|---|
| Main title | 18-20 | `true` | `RGB(0,51,102)` | 1 (center) |
| Section header | 13-16 | `true` | `RGB(40,40,40)` | 1 (center) |
| Body / box label | 10-12 | `false` | `RGB(50,50,50)` | 1 (center) |
| Small annotation | 8-10 | `false` | `RGB(100,100,100)` | 0 (left) |
| Arrow / flow label | 9-11 | `false` | `RGB(60,60,60)` | 1 (center) |

Default `fontSize` when omitted: **11pt** (was 8pt in earlier versions).

Font family recommendation:
- Chinese text: `"Microsoft YaHei"` or `"SimHei"`
- English text: `"Calibri"` or `"Segoe UI"`
- Code / model names: `"Consolas"`

## Layout Guidelines

| Element | Recommended size (px at 100 scale) |
|---|---|
| Canvas margin | 30-50 px on all sides |
| Gap between sibling boxes | 15-20 px |
| Gap between sections | 40-60 px |
| Arrow / connector width | 1.0-1.5 pt |
| Main container box height | 80-100 px |
| Sub-container box height | 55-70 px |
| Small badge / icon area | 60-80 x 60-80 px |
| Text box padding | implicit 6% via `TxtWidth = Width*0.94` |

Boxes in the same row or section should have **identical heights** for visual consistency.

## QA Checklist

- Page aspect ratio matches the reference image.
- Outer frames and major section dividers are drawn first and aligned.
- Chinese labels do not have ugly line breaks or overflow.
- Arrow directions match the reference.
- Dashed borders are visible but not heavier than content boxes.
- Preview file can be opened outside Visio.
- `.vsdx` consists of editable shapes, not a single pasted bitmap.
- Reference image is on a **separate** file, not embedded in the main page.
- Font sizes follow the typography hierarchy (title > header > body > label).
- Icon PNGs are placed at correct positions with proper sizing.
- No shape extends beyond the page boundaries.
- Gaps between boxes are at least 15 px (not 2-5 px).
