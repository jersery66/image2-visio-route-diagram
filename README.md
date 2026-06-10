# Image2 Visio Route Diagram

中文 | [English](#english)

一个用于生成模块化 Microsoft Visio 技术路线图的 Codex skill。它适合科研申报书技术路线图、arXiv 风格流程示意图、医学 AI 工作流图等场景，目标是在 `.vsdx` 中保留可编辑文字，而不是把整张图片粘进去冒充可编辑图。

核心思路：图标模块由 image2/image_gen 生成，所有说明文字由 Visio 文本框承载，边框、箭头、连接线等尽量使用 Visio 原生形状。

## 这个 Skill 约束什么

- 使用 image2/image_gen 生成“无文字”的图标模块。
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

## 仓库结构

```text
.
|-- SKILL.md
|-- agents/
|   `-- openai.yaml
`-- scripts/
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
3. 本地去除色键背景。
4. 裁出独立透明 PNG 图标模块（至少 512×512 px）。
5. 按版式坐标放入 Visio。
6. 所有文字都用 Visio 文本框添加。
7. 导出 PNG 预览，对比检查。
8. 检查 `.vsdx` 包结构，确认不是一张整图。
9. 确认 manifest 中所有 icon status 为 ok。

## 验证脚本

内置脚本可检查 Visio 文件是否具备模块化结构：

```powershell
python .\scripts\inspect_vsdx_structure.py .\output.vsdx --expect-single-page --min-media 5 --min-text 10 --forbid-reference --forbid-large-background-image
```

它会输出页数、媒体文件数量、形状数量、文本节点数量、是否存在参考页标记、页面尺寸，以及每个图片形状的面积占比。

可用参数：

| 参数 | 作用 |
|---|---|
| `--expect-single-page` | 期望只有一页（不含参考页） |
| `--min-media N` | 期望至少 N 个媒体文件 |
| `--min-text N` | 期望至少 N 个文本节点 |
| `--forbid-reference` | 不允许存在 `Original_Image_Reference` 标记 |
| `--forbid-large-background-image` | 检查是否有单张图片占据页面面积超过阈值 |
| `--max-image-area-ratio N` | 图片面积占比上限（默认 0.35，即 35 %） |

## 可编辑边界

图标本身是 image2 生成的 PNG 位图，因此图标绘制细节不是矢量可编辑的。可编辑部分包括 Visio 文本框、边框、箭头、徽标、连接线和布局形状。这个边界是有意保留的：它避免把生成式位图伪装成矢量图，同时满足申报书和论文修改中最重要的文字可编辑需求。

## 许可证

MIT。见 [LICENSE](LICENSE)。

---

## English

A Codex skill for building modular Microsoft Visio technical route diagrams from image2-generated icon modules. It is intended for grant-route figures, arXiv-style workflow schematics, medical AI technical-route diagrams, and similar figures where the final `.vsdx` must preserve editable text instead of becoming one pasted screenshot.

Core idea: image2/image_gen creates the no-text icon modules, Visio text boxes carry all labels and explanations, and native Visio shapes handle frames, arrows, connectors, and simple containers whenever possible.

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

## Repository Layout

```text
.
|-- SKILL.md
|-- agents/
|   `-- openai.yaml
`-- scripts/
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
3. Remove chroma-key backgrounds locally.
4. Crop individual transparent PNG icon modules (at least 512×512 px).
5. Place modules in Visio by layout coordinates.
6. Add all labels as editable Visio text boxes.
7. Export a preview PNG and visually compare.
8. Inspect the `.vsdx` package for modular structure.
9. Confirm all icons in the manifest have status `ok`.

## Validation Helper

The included script checks whether a Visio file looks structurally modular:

```powershell
python .\scripts\inspect_vsdx_structure.py .\output.vsdx --expect-single-page --min-media 5 --min-text 10 --forbid-reference --forbid-large-background-image
```

It reports page count, media count, shape count, text-node count, whether a reference-page marker is present, page dimensions, and the area ratio of every image shape.

Available flags:

| Flag | Purpose |
|---|---|
| `--expect-single-page` | Expect exactly one main page (no reference page) |
| `--min-media N` | Expect at least N media files |
| `--min-text N` | Expect at least N text nodes |
| `--forbid-reference` | Fail if `Original_Image_Reference` marker exists |
| `--forbid-large-background-image` | Fail if any single image occupies more than a threshold of the page area |
| `--max-image-area-ratio N` | Maximum allowed image-to-page area ratio (default 0.35, i.e. 35 %) |

## Editability Boundary

The icon artwork is raster PNG because it is generated by image2. The editable parts are the Visio text boxes, frames, arrows, badges, connectors, and layout shapes. This is intentional: the skill avoids pretending that generated bitmap icons are vector-editable, while preserving the text editing requirement that matters for proposal and manuscript revisions.

## License

MIT. See [LICENSE](LICENSE).
