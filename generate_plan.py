#!/usr/bin/env python3
"""Generate plan.json for the research framework diagram using PlanBuilder.

This is a CONCRETE EXAMPLE that demonstrates how to use the visio_plan_builder
library to assemble a complex academic research framework diagram.

Usage:
    python generate_plan.py
"""
import os
import sys

# Allow importing from the scripts/ subdirectory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))
from visio_plan_builder import PlanBuilder

pb = PlanBuilder(width=1600, height=1400, scale=100)
T = pb.theme

# ============================================================
# TITLE
# ============================================================
pb.title("面向司法矫治心理服务缺位的多模态感知智能体补位模式研究：整体框架")

# ============================================================
# SIDEBAR — 4 stages
# ============================================================
stages = [(60, "缺口识别"), (300, "机制构建"), (540, "场景验证"), (780, "模式形成")]
pb.stage_sidebar(stages)
pb.stage_sidebar_label("研究主线", "（四阶段）", y=1000)

# ============================================================
# TOP ROW — 现实场域与问题提出
# ============================================================
top_y, top_h = 60, 120
# Section header
pb.rect(160, top_y, 280, top_y + top_h,
        text="现实场域\n与问题提出", fontSize=12, bold=True,
        fill=T.context_fill, line=T.context_line, weight=1.2)

# Three content boxes
box_w, b1_x, b2_x, b3_x = 390, 290, 735, 1180

pb.content_box(b1_x, top_y, box_w, top_h,
               title="司法矫治场域特征",
               body_lines=["强约束、强管理、高敏感、低信任"],
               fill=T.context_fill, line=T.context_line, title_size=14)
pb.content_box(b2_x, top_y, box_w, top_h,
               title="心理服务现实困境",
               body_lines=["供给不足、识别滞后、干预断点、数据分散"],
               fill=T.context_fill, line=T.context_line, title_size=14)
pb.content_box(b3_x, top_y, box_w, top_h,
               title="核心问题",
               body_lines=["缺位在哪里？为何形成？", "AI如何补位而不越位？"],
               fill=T.context_fill, line=T.context_line, title_size=14)

# Inter-box arrows
mid = top_y + top_h // 2
for sx, ex in [(b1_x + box_w, b2_x), (b2_x + box_w, b3_x)]:
    pb.line(sx + 2, mid, ex - 2, mid, weight=1.5)

# ============================================================
# RESEARCH 1 — 缺口识别
# ============================================================
r1_y, r1_h, r1_x = 310, 230, 160
pb.section_header(r1_x, r1_y, 110, r1_h, "研究一：\n缺口识别")

b1_x1, b1_w = r1_x + 125, 420
pb.content_box(b1_x1, r1_y, b1_w, r1_h,
               title="① 心理服务现状与需求调查",
               body_lines=[
                   "研究对象：在押人员、社区矫正对象、\n司法工作人员、心理服务人员",
                   "调查内容：服务可及性、求助意愿、风险识别、\n缺位识别、干预需求、隐私顾虑",
               ], title_size=13)

# Tag row
tags = ["情感类", "知识类", "评估类", "支持类", "干预类", "发展类", "管理类"]
tag_colors = [
    "RGB(220,235,255)", "RGB(220,245,220)", "RGB(255,235,220)",
    "RGB(235,220,255)", "RGB(255,220,220)", "RGB(220,250,240)", "RGB(240,240,220)",
]
pb.tag_row(tags, tag_colors, b1_x1 + 12, r1_y + 100, caption="需求期望维度")

b2_x1, b2_w = b1_x1 + b1_w + 25, 420
pb.content_box(b2_x1, r1_y, b2_w, r1_h,
               title="② AI心理服务接受度与人机信任分析",
               body_lines=[
                   "认知基础：了解程度、信息来源、使用经验",
                   "接受意愿：使用态度、使用情境、行为倾向",
                   "信任基础：能力信任、伦理信任、责任信任",
                   "协同顾虑：隐私泄露、误判风险、责任不清",
               ], title_size=13)

b3_x1, b3_w = b2_x1 + b2_w + 25, 395
pb.rect(b3_x1, r1_y, b3_x1 + b3_w, r1_y + r1_h,
        fill=T.box_fill, line=T.box_line, weight=1.0, roundX=0.05)
pb.text_box(b3_x1 + 10, r1_y + 8, b3_x1 + b3_w - 10, r1_y + 30,
            "③ 场域缺位与成因分析", fontSize=13, bold=True, textColor="RGB(30,30,30)")

# Formula chain
pb.formula_chain(
    [("现实需求", "RGB(220,230,250)", "RGB(80,100,160)"),
     ("现状供给", "RGB(220,230,250)", "RGB(80,100,160)"),
     ("缺位表现", "RGB(255,225,225)", "RGB(180,80,80)")],
    x=b3_x1 + 25, y=r1_y + 38,
)

pb.text_box(b3_x1 + 10, r1_y + 75, b3_x1 + b3_w - 10, r1_y + 100,
            "成因分析：主体关系、资源配置、\n风险感知、服务机制、数据治理",
            fontSize=9, textColor=T.body_text)
pb.text_box(b3_x1 + 10, r1_y + 105, b3_x1 + b3_w - 10, r1_y + 130,
            "输出结果：缺位清单、成因解释、补位边界",
            fontSize=9, textColor=T.body_text)

# Arrows between R1 boxes
mid_y = r1_y + r1_h // 2
for sx, ex in [(b1_x1 + b1_w, b2_x1), (b2_x1 + b2_w, b3_x1)]:
    pb.line(sx + 2, mid_y, ex - 2, mid_y, weight=1.3)

# ============================================================
# RESEARCH 2 — 机制构建
# ============================================================
r2_y = r1_y + r1_h + 30
r2_h = 310
pb.section_header(r1_x, r2_y, 110, r2_h, "研究二：\n机制构建")

# Top pathway
path_y = r2_y + 10
path_x = r1_x + 125
step_w, path_h, step_gap = 155, 75, 22
arrow_w = 18

pb.rect(path_x, path_y, path_x + step_w, path_y + path_h,
        text="风险感知\n补位路径", fontSize=11, bold=True,
        fill="RGB(220,235,255)", line="RGB(60,100,180)", weight=1.0, roundX=0.04)

s2_x = path_x + step_w + arrow_w + step_gap
pb.content_box(s2_x, path_y, step_w, path_h,
               title="多源线索采集", title_size=11, body_size=8,
               body_lines=["文本|语音|表情|行为|量表", "人机协同(专业主导下协同)"])

s3_x = s2_x + step_w + arrow_w + step_gap
pb.content_box(s3_x, path_y, step_w, path_h,
               title="主客观一致性校验", title_size=11, body_size=8,
               body_lines=["主观表达 ↔ 客观反应", "历史状态"])

s4_x = s3_x + step_w + arrow_w + step_gap
pb.content_box(s4_x, path_y, step_w, path_h,
               title="分级预警", title_size=11,
               body_lines=["（低/中/高/危机）"],
               fill=T.orange_fill, line=T.orange_line,
               body_color="RGB(120,80,40)")

# Top pathway arrows
for sx, ex in [(path_x + step_w, s2_x), (s2_x + step_w, s3_x), (s3_x + step_w, s4_x)]:
    pb.line(sx + 2, path_y + path_h // 2, ex - 2, path_y + path_h // 2)

# Bottom pathway
path2_y = path_y + path_h + 22
pb.rect(path_x, path2_y, path_x + step_w, path2_y + path_h,
        text="干预支持\n补位路径", fontSize=11, bold=True,
        fill="RGB(220,245,220)", line="RGB(60,140,60)", weight=1.0, roundX=0.04)

pb.content_box(s2_x, path2_y, step_w, path_h,
               title="分级干预匹配", title_size=11, body_size=8,
               body_lines=["心理支持|重点关注|专业转介"],
               fill=T.green_fill, line=T.green_line, body_color=T.green_text)
pb.content_box(s3_x, path2_y, step_w, path_h,
               title="人工复核处置", title_size=11, body_size=8,
               body_lines=["民警初核|专业复核|转介", "处置"],
               fill=T.green_fill, line=T.green_line, body_color=T.green_text)
pb.content_box(s4_x, path2_y, step_w, path_h,
               title="动态优化", title_size=11, body_size=8,
               body_lines=["（效果反馈、模型修正、", "策略优化）"],
               fill=T.green_fill, line=T.green_line, body_color=T.green_text)

# Bottom pathway arrows
for sx, ex in [(path_x + step_w, s2_x), (s2_x + step_w, s3_x), (s3_x + step_w, s4_x)]:
    pb.line(sx + 2, path2_y + path_h // 2, ex - 2, path2_y + path_h // 2)

# Convergence arrows
for cx in [s4_x + step_w // 2, s3_x + step_w // 2]:
    pb.line(cx, path_y + path_h + 2, cx, path2_y - 2, weight=1.0)

# Mechanism box
mech_x = s4_x + step_w + 40
mech_w, mech_h = 340, r2_h - 20
pb.rect(mech_x, r2_y + 10, mech_x + mech_w, r2_y + 10 + mech_h,
        fill=T.mech_fill, line=T.mech_line, weight=1.4, dash=True, roundX=0.06)

pb.text_box(mech_x + 15, r2_y + 22, mech_x + mech_w - 15, r2_y + 48,
            "多模态感知", fontSize=14, bold=True, textColor="RGB(60,40,120)")
pb.text_box(mech_x + 15, r2_y + 46, mech_x + mech_w - 15, r2_y + 70,
            "智能体补位机制", fontSize=14, bold=True, textColor="RGB(60,40,120)")

pb.text_box(mech_x + 15, r2_y + 85, mech_x + mech_w - 15, r2_y + 108,
            "连续感知和证据追溯", fontSize=10, textColor=T.body_text)
pb.text_box(mech_x + 15, r2_y + 110, mech_x + mech_w - 15, r2_y + 133,
            "人工复核×分级处置", fontSize=10, textColor=T.body_text)

constraint_y = r2_y + 155
pb.rect(mech_x + 15, constraint_y, mech_x + mech_w - 15, constraint_y + 28,
        text="技术可行 × 专业可用 ×", fontSize=10, bold=True,
        fill="RGB(235,230,250)", line="RGB(120,100,180)", weight=0.8, roundX=0.04)
pb.rect(mech_x + 15, constraint_y + 33, mech_x + mech_w - 15, constraint_y + 61,
        text="安全可控 × 责任可界定", fontSize=10, bold=True,
        fill="RGB(235,230,250)", line="RGB(120,100,180)", weight=0.8, roundX=0.04)

# Arrows to mechanism box
for py in [path_y + path_h // 2, path2_y + path_h // 2]:
    pb.line(s4_x + step_w + 2, py, mech_x - 2, py, weight=1.2)

pb.text_box(mech_x + 60, r2_y + mech_h - 12, mech_x + mech_w - 60, r2_y + mech_h + 8,
            "持续迭代", fontSize=9, textColor="RGB(100,80,140)", bold=True)

# ============================================================
# RESEARCH 3 — 场景验证
# ============================================================
r3_y = r2_y + r2_h + 30
r3_h = 230
pb.section_header(r1_x, r3_y, 110, r3_h, "研究三：\n场景验证")

r3_box_w, r3_gap, r3_start = 310, 28, r1_x + 125
r3_boxes = [
    ("① 分场景与分群体试点",
     ["场景：监管场所、社区矫正、\n戒毒矫治等", "群体：新入矫、重点关注、临近\n解矫、不同风险等级对象"]),
    ("② 识别一致性与预警效度评价",
     ["一致性：AI输出—人工评估—\n量表比对", "有效性：风险识别、预警分级、\n证据命中"]),
    ("③ 服务效果与安全性评价",
     ["响应效果：复核效率、干预匹配\n跟踪反馈", "安全边界：隐私保护、误判纠偏\n危机转介、责任归属"]),
    ("④ 适用条件与运行边界",
     ["适用场景、适用对象、人工介入条件", "不直替代事项、伦理风险保障机制"]),
]

r3_positions = []
cx = r3_start
for title, body in r3_boxes:
    pb.content_box(cx, r3_y, r3_box_w, r3_h, title=title,
                   body_lines=body, title_size=12)
    r3_positions.append(cx)
    cx += r3_box_w + r3_gap + 25

r3_mid = r3_y + r3_h // 2
for i in range(len(r3_positions) - 1):
    sx = r3_positions[i] + r3_box_w
    ex = r3_positions[i + 1]
    pb.line(sx + 2, r3_mid, ex - 2, r3_mid, weight=1.2)

# ============================================================
# RESEARCH 4 — 模式形成
# ============================================================
r4_y = r3_y + r3_h + 30
r4_h = 200
pb.section_header(r1_x, r4_y, 110, r4_h, "成果集成：\n模式形成")

title_bar_y = r4_y + 5
pb.rect(r1_x + 125, title_bar_y, r1_x + 125 + 1270, title_bar_y + 35,
        text="形成可复制、可评估、可监管的司法矫治心理服务补位模式",
        fontSize=13, bold=True, fill="RGB(220,230,245)", line=T.context_line,
        weight=1.2, roundX=0.04)

out_w, out_gap = 400, 35
out_y = title_bar_y + 50
out_h = r4_h - 60
out_start = r1_x + 145
outputs = [
    ("补位模式与实施流程", "适用场景、操作流程、人工介入节点工具集\n与数据规范"),
    ("评价指标与复核规范", "风险识别、预警分级、证据追溯、安全审核\n指标体系、数据与评估标准"),
    ("应用边界与治理建议", "责任划分、隐私保护、转介衔接、制度优化\n政策建议与推广路径"),
]
out_positions = []
cx = out_start
for title, body in outputs:
    pb.content_box(cx, out_y, out_w, out_h, title=title, body_lines=[body],
                   title_size=12, fill=T.output_fill, line=T.output_line)
    out_positions.append(cx)
    cx += out_w + out_gap

out_mid = out_y + out_h // 2
for i in range(len(out_positions) - 1):
    sx = out_positions[i] + out_w
    ex = out_positions[i + 1]
    pb.line(sx + 2, out_mid, ex - 2, out_mid, weight=1.2)

pb.line(out_start + 635, title_bar_y + 37, out_start + 635, out_y - 2, weight=1.0)

# ============================================================
# FEEDBACK LOOPS
# ============================================================
pb.feedback_loop(
    from_y=r4_y + r4_h // 2,
    to_y=r2_y + r2_h // 2,
    main_label="反馈优化",
    sub_label="(实践反馈优化)",
)
pb.feedback_loop(
    from_y=r4_y + r4_h + 10,
    to_y=r1_y + r1_h + 5,
    main_label="反哺识别",
    sub_label="(迭代更新)",
)

# ============================================================
# SAVE
# ============================================================
out_path = os.path.join(os.path.dirname(__file__), "plan.json")
pb.save(out_path, name="研究框架整体图")
