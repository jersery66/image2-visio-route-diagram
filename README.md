# Image2 Visio Route Diagram

A Codex / QoderWork skill for creating modular Microsoft Visio technical route diagrams with image2-generated icon modules, editable Visio text, and PowerShell COM automation.

## What It Does

Generates arXiv / Nature-style technical route diagrams as editable `.vsdx` files by combining:

- **image2 icon generation** — transparent no-text PNG icon modules with chroma-key background removal.
- **Visio COM automation** — deterministic `.vsdx` creation from a JSON plan via `create_visio_from_plan.ps1`.
- **Structural validation** — VSDX package inspection via `inspect_vsdx_structure.py`.

## Included Files

| File | Purpose |
|---|---|
| `SKILL.md` | Main skill instructions and workflow. |
| `agents/openai.yaml` | Marketplace display metadata. |
| `references/plan_schema_and_qa.md` | JSON plan schema and QA checklist. |
| `scripts/check_visio_environment.ps1` | Visio / COM / export tool environment checker. |
| `scripts/create_visio_from_plan.ps1` | Generates editable `.vsdx` from a JSON plan. |
| `scripts/inspect_vsdx_structure.py` | VSDX package validator (read-only). |

## Quick Start

1. Provide a reference image of the desired route diagram.
2. The skill generates icon modules via image2, builds a JSON layout plan, and runs the Visio generation script.
3. Output: editable `.vsdx`, PNG preview, icon manifest, and validation report.

## Requirements

- Windows with Microsoft Visio installed.
- PowerShell 5.1+ (Windows PowerShell).
- Python 3 (with `pywin32` for COM automation if needed).
- Optional: LibreOffice / `pdftoppm` for PNG export fallback.

## Key Improvements Over Previous Versions

- **Stable output**: JSON plan + PowerShell script = deterministic, reproducible results.
- **Typography standards**: explicit font hierarchy (title 18-20pt, header 13-16pt, body 10-12pt).
- **Layout standards**: minimum 15-20px gaps, consistent box heights, proper margins.
- **No overwrite bug**: reference image stays external, validation is read-only, `-BackupExisting` flag protects output.
- **Image shape type**: place transparent PNG icons at exact coordinates in the JSON plan.
- **Rounded corners**: optional `roundX` parameter for modern-looking containers.

## License

MIT License, Copyright 2026 Jersery.
