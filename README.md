# Image2 Visio Route Diagram

中文 | [English](#english)

一个用于生成模块化 Microsoft Visio 技术路线图的 Codex / QoderWork skill。适合科研申报书技术路线图、arXiv 风格流程示意图、医学 AI 工作流图等场景，目标是在 `.vsdx` 中保留可编辑文字，而不是把整张图片粘进去冒充可编辑图。

核心思路：图标模块由 image2/image_gen 生成，所有说明文字由 Visio 文本框承载，边框、箭头、连接线等尽量使用 Visio 原生形状。通过 JSON 计划 + PowerShell COM 自动化脚本确定性生成 `.vsdx`，保证输出稳定可复现。

## 这个 Skill 约束什么

- 使用 image2/image_gen 生成"无文字"的图标模块。
- 不从完整路线图截图里扣图标。
- 当用户要求 image2 图标时，不用代码手绘内容图标替代。
- 所有标签和说明文字都放在可编辑的 Visio 文本框中。
- 边框、箭头、徽标、容器等可使用 Visio 原生形状。
- 根据图标主色选择安全色键。绿色模块应使用洋红 `#ff00ff`，不要用绿色背景。
- 最终交付物不保留 `Original_Image_Reference` 参考页或整图背景。
- 声称文件可编辑前，先检查 `.vsdx` 包结构。
- 不从完整路线图截图中裁剪图标；只从专用 icon sprite sheet 裁剪。
- 低清路线图截图只能作为语义参考，不能高清化后直接复用。
- 图标有明显缺陷（模糊、色晕、文字残留、语义错误）时重新生成，不做后期修补。
- 主 `.vsdx` 只由脚本生成一次，校验阶段不重写文件；已有输出文件时用 `-BackupExisting` 自动备份。

## 仓库结构

```text
.
|-- SKILL.md
|-- README.md
|-- LICENSE
|-- agents/
|   `-- openai.yaml
|-- references/
|   `-- plan_schema_and_qa.md
`-- scripts/
    |-- check_visio_environment.ps1
    |-- create_visio_from_plan.ps1
    `-- inspect_vsdx_structure.py
```

## 安装

将仓库克隆到 Codex skills 目录：

```powershell
git clone https://github.com/jersery66/image2-visio-route-diagram.git "$env:USERPROFILE\.codex\skills\image2-visio-route-diagram"
```

重启 Codex 会话后，skill 元数据会被自动发现。

## 使用

可以显式要求 Codex 使用该 skill：

```text
Use $image2-visio-route-diagram to create a modular Visio route diagram with image2-generated no-text icons and editable text.
```

推荐流程：

1. 整理路线图大纲和版式，生成图标清单 manifest（含 icon_id、meaning、prompt、key_color、placement）。
2. 用 image2/image_gen 按 manifest 生成独立无字图标或 sprite sheet。
3. 本地去除色键背景，裁出独立透明 PNG 图标模块（至少 512×512 px）。
4. 构建 JSON 布局计划（页面尺寸、图形坐标、文字样式、图标位置），参考 `references/plan_schema_and_qa.md`。
5. 运行 `scripts/create_visio_from_plan.ps1` 生成 `.vsdx`。
6. 所有文字都用 Visio 文本框添加（脚本自动处理）。
7. 导出 PNG 预览，对比检查。
8. 运行 `scripts/inspect_vsdx_structure.py` 检查 `.vsdx` 包结构。
9. 确认 manifest 中所有 icon status 为 ok。

## 内置脚本

### `scripts/create_visio_from_plan.ps1`

根据 JSON 计划创建可编辑 `.vsdx` 文件。支持矩形、椭圆、文本框、直线、折线、图片（PNG 图标）六种图形类型。

```powershell
powershell -File scripts/create_visio_from_plan.ps1 `
  -PlanPath plan.json `
  -OutVsdx output.vsdx `
  -OutPng preview.png `
  -BackupExisting
```

参数说明：

| 参数 | 作用 |
|---|---|
| `-PlanPath` | JSON 计划文件路径（必需） |
| `-OutVsdx` | 输出 `.vsdx` 文件路径（必需） |
| `-OutEmf` | 可选，导出 EMF 矢量预览 |
| `-OutPng` | 可选，导出 PNG 预览（失败时回退到 EMF） |
| `-Visible` | 显示 Visio 窗口（默认后台运行） |
| `-KeepVisioOpen` | 生成后不关闭 Visio |
| `-BackupExisting` | 输出文件已存在时自动创建时间戳备份 |

### `scripts/check_visio_environment.ps1`

检查 Visio 安装、COM 自动化、导出和转换工具是否可用。

```powershell
powershell -File scripts/check_visio_environment.ps1 -TryCom
```

### `scripts/inspect_vsdx_structure.py`

检查 Visio 文件是否具备模块化结构（只读，不修改文件）。

```powershell
python scripts/inspect_vsdx_structure.py output.vsdx --expect-single-page --min-media 5 --min-text 10 --min-image-shapes 5 --min-native-shapes 10 --forbid-reference --forbid-large-background-image
```

可用参数：

| 参数 | 作用 |
|---|---|
| `--expect-single-page` | 期望只有一页（不含参考页） |
| `--min-media N` | 期望至少 N 个媒体文件 |
| `--min-text N` | 期望至少 N 个文本节点 |
| `--min-image-shapes N` | 期望页面上至少 N 个图片形状 |
| `--min-native-shapes N` | 期望至少 N 个原生 Visio 形状（非图片） |
| `--forbid-reference` | 不允许存在 `Original_Image_Reference` 标记 |
| `--forbid-large-background-image` | 检查是否有单张图片占据页面面积超过阈值 |
| `--max-image-area-ratio N` | 图片面积占比上限（默认 0.35，即 35%） |

## 排版标准

技能内置字体层级和布局规范，确保输出一致：

| 角色 | 字号 | 粗体 | 字色 | 对齐 |
|---|---|---|---|---|
| 主标题 | 18-20pt | 是 | 深蓝 | 居中 |
| 节标题 | 13-16pt | 是 | 深灰 | 居中 |
| 正文/框内标签 | 10-12pt | 否 | 灰色 | 居中 |
| 小注释 | 8-10pt | 否 | 浅灰 | 左对齐 |

布局间距：同级框间距 15-20px，节间距 40-60px，画布边距 30-50px。

## 最终交付物

每次最终交付应包含：

- **可编辑 `.vsdx` 文件** — 主 Visio 文件，包含原生形状和文本框。
- **PNG 预览图** — 主页面渲染导出，方便快速视觉审查。
- **`icon_manifest.json`** — 图标清单，记录每个图标的 icon_id、meaning、prompt、key_color、file、placement、status。
- **验证脚本输出** — `inspect_vsdx_structure.py` 的完整 JSON 结果和通过/失败摘要。

这四样产物让你以后可以定位和重新生成某个图标，而不需要反向拆解 `.vsdx`。

## 可编辑边界

图标本身是 image2 生成的 PNG 位图，因此图标绘制细节不是矢量可编辑的。可编辑部分包括 Visio 文本框、边框、箭头、徽标、连接线和布局形状。这个边界是有意保留的：它避免把生成式位图伪装成矢量图，同时满足申报书和论文修改中最重要的文字可编辑需求。

## 更新日志

### v1.4.0 — 2026-07-14

融合 `codex-visio-replica-workflow` 技能，解决输出不稳定、字体排版、校验覆盖三大问题。

- 新增 `create_visio_from_plan.ps1`：JSON 计划驱动的确定性 Visio 生成
- 新增 `image` 图形类型：在 JSON 计划中放置透明 PNG 图标
- 新增字体层级标准（标题 18-20pt、节标题 13-16pt、正文 10-12pt）
- 新增布局间距标准（同级框 15-20px、节间距 40-60px）
- 修复校验覆盖 bug：参考图不嵌入主文件、校验只读、`-BackupExisting` 自动备份
- 新增 `check_visio_environment.ps1` 环境检查脚本
- 新增 `references/plan_schema_and_qa.md` JSON 计划模式文档
- 新增圆角支持（`roundX` 参数）和 PNG 导出（`-OutPng`）

### v1.3.0 — 2026-07-07

- 新增单图标 vs. sprite sheet 决策规则
- 新增 `--min-image-shapes` 和 `--min-native-shapes` 校验参数
- 新增最终交付物要求（4 项产物）

### v1.2.0 — 2026-07-07

- 新增图标资产策略（三级策略）
- 新增故障恢复表（6 种症状）
- 新增 `--forbid-large-background-image` 校验

### v1.1.0 — 2026-07-07

- 新增中英双语 README

### v1.0.0 — 2026-07-07

- 初始版本发布

## 许可证

MIT。见 [LICENSE](LICENSE)。

---

## English

A Codex / QoderWork skill for building modular Microsoft Visio technical route diagrams from image2-generated icon modules. Intended for grant-route figures, arXiv-style workflow schematics, medical AI technical-route diagrams, and similar figures where the final `.vsdx` must preserve editable text instead of becoming one pasted screenshot.

Core idea: image2/image_gen creates the no-text icon modules, Visio text boxes carry all labels and explanations, and native Visio shapes handle frames, arrows, connectors, and simple containers. A JSON plan + PowerShell COM automation script produces the `.vsdx` deterministically for stable, reproducible output.

## What This Skill Enforces

- Generate no-text icon modules with image2/image_gen.
- Do not crop icons from a full rendered route-diagram screenshot.
- Do not hand-draw content icons when the user asked for image2-generated icons.
- Keep all labels and explanations as editable Visio text boxes.
- Use native Visio shapes for frames, arrows, badges, and simple containers.
- Use a safe chroma key per icon color. Green modules should use magenta `#ff00ff`, not green.
- Do not leave an `Original_Image_Reference` page or whole-image background in the final deliverable.
- Verify the `.vsdx` structure before claiming the file is editable.
- Do not crop icons from a full rendered route-diagram screenshot; crop only from a dedicated icon sprite sheet.
- Low-resolution route-diagram screenshots may be used only as semantic references — do not upscale and reuse them as final assets.
- Regenerate defective icons (blurry, haloed, text residue, wrong semantics) instead of patching them in post-processing.
- The main `.vsdx` is written exactly once by the script; validation never overwrites it. Use `-BackupExisting` when the output file already exists.

## Repository Layout

```text
.
|-- SKILL.md
|-- README.md
|-- LICENSE
|-- agents/
|   `-- openai.yaml
|-- references/
|   `-- plan_schema_and_qa.md
`-- scripts/
    |-- check_visio_environment.ps1
    |-- create_visio_from_plan.ps1
    `-- inspect_vsdx_structure.py
```

## Install

Clone this repository into your Codex skills directory:

```powershell
git clone https://github.com/jersery66/image2-visio-route-diagram.git "$env:USERPROFILE\.codex\skills\image2-visio-route-diagram"
```

Restart the Codex session so the skill metadata is discovered.

## Usage

Ask Codex to use the skill explicitly:

```text
Use $image2-visio-route-diagram to create a modular Visio route diagram with image2-generated no-text icons and editable text.
```

Expected workflow:

1. Draft the route layout and produce an icon manifest (icon_id, meaning, prompt, key_color, placement).
2. Generate icon modules or module sprite sheets with image2/image_gen, following the manifest.
3. Remove chroma-key backgrounds locally. Crop individual transparent PNG icon modules (at least 512×512 px).
4. Build a JSON layout plan (page size, shape coordinates, text styles, icon positions). See `references/plan_schema_and_qa.md`.
5. Run `scripts/create_visio_from_plan.ps1` to generate the `.vsdx`.
6. All text is handled by the script as editable Visio text boxes.
7. Export a preview PNG and visually compare.
8. Run `scripts/inspect_vsdx_structure.py` to inspect the `.vsdx` package.
9. Confirm all icons in the manifest have status `ok`.

## Built-in Scripts

### `scripts/create_visio_from_plan.ps1`

Creates an editable `.vsdx` from a JSON plan. Supports six shape types: rect, oval, text, line, polyline, and image (PNG icon placement).

```powershell
powershell -File scripts/create_visio_from_plan.ps1 `
  -PlanPath plan.json `
  -OutVsdx output.vsdx `
  -OutPng preview.png `
  -BackupExisting
```

Parameters:

| Parameter | Purpose |
|---|---|
| `-PlanPath` | JSON plan file path (required) |
| `-OutVsdx` | Output `.vsdx` file path (required) |
| `-OutEmf` | Optional: export EMF vector preview |
| `-OutPng` | Optional: export PNG preview (falls back to EMF on failure) |
| `-Visible` | Show Visio window (runs in background by default) |
| `-KeepVisioOpen` | Do not close Visio after generation |
| `-BackupExisting` | Auto-create timestamped backup when output file already exists |

### `scripts/check_visio_environment.ps1`

Checks whether Visio, COM automation, and export/conversion tools are available.

```powershell
powershell -File scripts/check_visio_environment.ps1 -TryCom
```

### `scripts/inspect_vsdx_structure.py`

Checks whether a Visio file looks structurally modular (read-only, does not modify the file).

```powershell
python scripts/inspect_vsdx_structure.py output.vsdx --expect-single-page --min-media 5 --min-text 10 --min-image-shapes 5 --min-native-shapes 10 --forbid-reference --forbid-large-background-image
```

Available flags:

| Flag | Purpose |
|---|---|
| `--expect-single-page` | Expect exactly one main page (no reference page) |
| `--min-media N` | Expect at least N media files |
| `--min-text N` | Expect at least N text nodes |
| `--min-image-shapes N` | Expect at least N image shapes on the page |
| `--min-native-shapes N` | Expect at least N native (non-image) Visio shapes |
| `--forbid-reference` | Fail if `Original_Image_Reference` marker exists |
| `--forbid-large-background-image` | Fail if any single image occupies more than a threshold of the page area |
| `--max-image-area-ratio N` | Maximum allowed image-to-page area ratio (default 0.35, i.e. 35%) |

## Typography Standards

The skill enforces a font hierarchy and layout spacing for consistent output:

| Role | Size | Bold | Color | Align |
|---|---|---|---|---|
| Main title | 18-20pt | Yes | Dark blue | Center |
| Section header | 13-16pt | Yes | Dark gray | Center |
| Body / box label | 10-12pt | No | Gray | Center |
| Small annotation | 8-10pt | No | Light gray | Left |

Layout spacing: 15-20px between sibling boxes, 40-60px between sections, 30-50px canvas margin.

## Final Delivery

Every deliverable must include:

- **Editable `.vsdx` file** — the main Visio diagram with native shapes and text boxes.
- **PNG preview** — a rendered export of the main page for quick visual review.
- **`icon_manifest.json`** — the manifest documenting all icon modules (icon_id, meaning, prompt, key_color, file, placement, status).
- **Validation output** — the full JSON result and pass/fail summary from `inspect_vsdx_structure.py`.

These four artifacts let you re-generate or repair individual icons later without reverse-engineering the `.vsdx`.

## Editability Boundary

The icon artwork is raster PNG because it is generated by image2. The editable parts are the Visio text boxes, frames, arrows, badges, connectors, and layout shapes. This is intentional: the skill avoids pretending that generated bitmap icons are vector-editable, while preserving the text editing requirement that matters for proposal and manuscript revisions.

## Changelog

### v1.4.0 — 2026-07-14

Merged `codex-visio-replica-workflow` skill to fix output instability, font/layout issues, and validation overwrite bug.

- New `create_visio_from_plan.ps1`: deterministic Visio generation driven by JSON plan
- New `image` shape type: place transparent PNG icons via JSON plan
- Typography standards (title 18-20pt, header 13-16pt, body 10-12pt)
- Layout spacing standards (15-20px gaps, 40-60px section gaps)
- Fixed overwrite bug: reference image stays external, validation is read-only, `-BackupExisting` auto-backup
- New `check_visio_environment.ps1` environment checker
- New `references/plan_schema_and_qa.md` JSON plan schema reference
- Rounded corners (`roundX`) and PNG export (`-OutPng`)

### v1.3.0 — 2026-07-07

- Add single-icon vs. sprite-sheet decision rule
- Add `--min-image-shapes` and `--min-native-shapes` validation checks
- Add final-delivery requirements (4 artifacts)

### v1.2.0 — 2026-07-07

- Add icon asset policy (3-tier strategy)
- Add failure recovery table (6 symptoms)
- Add `--forbid-large-background-image` validation check

### v1.1.0 — 2026-07-07

- Add bilingual README (Chinese + English)

### v1.0.0 — 2026-07-07

- Initial skill release

## License

MIT. See [LICENSE](LICENSE).
