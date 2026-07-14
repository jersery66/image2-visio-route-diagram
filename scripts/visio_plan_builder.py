#!/usr/bin/env python3
"""Reusable layout primitives for building Visio JSON plans.

Import this module in any plan-generation script:

    from visio_plan_builder import PlanBuilder

    pb = PlanBuilder(width=1600, height=1400)
    pb.title("My Diagram Title", fontSize=20)
    pb.section_header(x=160, y=300, w=110, h=230, label="Section 1")
    pb.content_box(x=285, y=300, w=420, h=230, title="Box Title",
                   body_lines=["Line 1", "Line 2"])
    pb.save("plan.json")
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ── Colour presets ──────────────────────────────────────────────────────────
@dataclass(frozen=True)
class Theme:
    """Predefined colour palette for consistent diagrams."""
    # Section headers
    header_fill: str = "RGB(20,60,120)"
    header_text: str = "RGB(255,255,255)"
    # Content boxes
    box_fill: str = "RGB(245,248,255)"
    box_line: str = "RGB(100,120,180)"
    # Top-row context boxes
    context_fill: str = "RGB(240,245,255)"
    context_line: str = "RGB(88,103,150)"
    # Title
    title_color: str = "RGB(0,51,102)"
    # Body text
    body_text: str = "RGB(60,60,60)"
    # Arrows
    arrow_weight: float = 1.2
    # Green pathway
    green_fill: str = "RGB(240,252,240)"
    green_line: str = "RGB(80,140,80)"
    green_text: str = "RGB(60,100,60)"
    # Orange highlight
    orange_fill: str = "RGB(255,240,220)"
    orange_line: str = "RGB(180,120,60)"
    # Mechanism / dashed box
    mech_fill: str = "RGB(248,245,255)"
    mech_line: str = "RGB(100,80,160)"
    # Output boxes
    output_fill: str = "RGB(240,248,240)"
    output_line: str = "RGB(80,140,80)"
    # Feedback loop labels
    feedback_text: str = "RGB(60,120,60)"
    feedback_sub: str = "RGB(80,140,80)"


DEFAULT_THEME = Theme()


# ── PlanBuilder ─────────────────────────────────────────────────────────────
class PlanBuilder:
    """Accumulates shapes and exports a Visio JSON plan.

    Parameters
    ----------
    width, height : int
        Canvas dimensions in pixels.
    scale : int
        Pixels per inch (default 100).
    theme : Theme
        Colour palette (uses DEFAULT_THEME if omitted).
    """

    def __init__(
        self,
        width: int = 1600,
        height: int = 1400,
        scale: int = 100,
        theme: Theme | None = None,
    ):
        self.width = width
        self.height = height
        self.scale = scale
        self.theme = theme or DEFAULT_THEME
        self.shapes: list[dict[str, Any]] = []

    # ── Low-level shape primitives ──────────────────────────────────────

    def rect(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        text: str = "",
        fill: str = "RGB(255,255,255)",
        line: str = "RGB(35,35,35)",
        weight: float = 1.0,
        dash: bool = False,
        fontSize: float = 11,
        textColor: str = "RGB(40,40,40)",
        bold: bool = False,
        align: int = 1,
        fontFamily: str = "Microsoft YaHei",
        roundX: float = 0,
        noFill: bool = False,
        noLine: bool = False,
    ) -> dict:
        """Add a rectangle shape. Returns the shape dict."""
        s: dict[str, Any] = {
            "type": "rect",
            "x1": x1, "y1": y1, "x2": x2, "y2": y2,
            "style": {
                "fill": fill, "line": line, "weight": weight, "dash": dash,
                "fontSize": fontSize, "textColor": textColor, "bold": bold,
                "align": align, "fontFamily": fontFamily, "roundX": roundX,
                "noFill": noFill, "noLine": noLine,
            },
        }
        if text:
            s["text"] = text
        self.shapes.append(s)
        return s

    def text_box(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        text: str,
        fontSize: float = 11,
        textColor: str = "RGB(40,40,40)",
        bold: bool = False,
        align: int = 1,
        fontFamily: str = "Microsoft YaHei",
    ) -> None:
        """Add a text-only shape (no fill, no border)."""
        self.shapes.append({
            "type": "text",
            "x1": x1, "y1": y1, "x2": x2, "y2": y2,
            "text": text,
            "style": {
                "fontSize": fontSize, "textColor": textColor,
                "bold": bold, "align": align, "fontFamily": fontFamily,
            },
        })

    def line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        weight: float = 1.2,
        arrow: str = "end",
        dash: bool = False,
        lineColor: str = "RGB(35,35,35)",
    ) -> None:
        """Add a straight line (optionally with arrowhead)."""
        self.shapes.append({
            "type": "line",
            "x1": x1, "y1": y1, "x2": x2, "y2": y2,
            "arrow": arrow,
            "style": {"weight": weight, "dash": dash, "line": lineColor, "noFill": True},
        })

    def polyline(
        self,
        points: list[list[float]],
        weight: float = 1.2,
        arrow: str = "end",
        dash: bool = False,
        noFill: bool = False,
        lineColor: str = "RGB(35,35,35)",
    ) -> None:
        """Add a multi-segment polyline."""
        self.shapes.append({
            "type": "polyline",
            "points": points,
            "arrow": arrow,
            "style": {"weight": weight, "dash": dash, "noFill": noFill, "line": lineColor},
        })

    def image(
        self,
        filePath: str,
        x: float,
        y: float,
        widthPx: float,
        heightPx: float | None = None,
    ) -> None:
        """Place a transparent PNG icon on the page (center-positioned)."""
        self.shapes.append({
            "type": "image",
            "filePath": filePath,
            "x": x, "y": y,
            "widthPx": widthPx,
            "heightPx": heightPx or widthPx,
        })

    # ── Higher-level layout primitives ──────────────────────────────────

    def title(
        self,
        text: str,
        x1: float = 100,
        y1: float = 8,
        x2: float = 1500,
        y2: float = 42,
        fontSize: float = 20,
        bold: bool = True,
        textColor: str | None = None,
    ) -> None:
        """Add a page title text box."""
        self.text_box(
            x1, y1, x2, y2, text,
            fontSize=fontSize, bold=bold,
            textColor=textColor or self.theme.title_color,
        )

    def section_header(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        label: str,
        fill: str | None = None,
        textColor: str | None = None,
        fontSize: float = 14,
        roundX: float = 0.06,
    ) -> None:
        """Add a dark section header rectangle with white text."""
        self.rect(
            x, y, x + w, y + h,
            text=label,
            fill=fill or self.theme.header_fill,
            textColor=textColor or self.theme.header_text,
            bold=True, fontSize=fontSize, roundX=roundX,
        )

    def stage_sidebar(
        self,
        stages: list[tuple[float, str]],
        x1: float = 12,
        x2: float = 148,
        fill: str | None = None,
        textColor: str | None = None,
        fontSize: float = 15,
    ) -> None:
        """Draw a vertical column of stage labels with down-arrows.

        Parameters
        ----------
        stages : list of (y_top, label) tuples
        """
        fill = fill or self.theme.header_fill
        textColor = textColor or self.theme.header_text
        stage_h = stages[0][0]  # first y position = height of each stage box

        for i, (sy, label) in enumerate(stages):
            # Calculate box height from gap to next stage or default
            if i + 1 < len(stages):
                box_h = stages[i + 1][0] - sy - 40  # 40px gap for arrow
            else:
                box_h = 200  # default for last stage
            self.rect(
                x1, sy, x2, sy + box_h,
                text=label, fill=fill, textColor=textColor,
                bold=True, fontSize=fontSize, roundX=0.08,
            )
            # Down-arrow to next stage
            if i + 1 < len(stages):
                cy = sy + box_h
                ny = stages[i + 1][0]
                self.line(
                    (x1 + x2) / 2, cy + 2,
                    (x1 + x2) / 2, ny - 2,
                    weight=1.5, arrow="end",
                )

    def stage_sidebar_label(
        self,
        main_text: str,
        sub_text: str,
        x1: float = 5,
        x2: float = 155,
        y: float = 1000,
    ) -> None:
        """Add sidebar description labels below all sidebar boxes."""
        self.text_box(x1, y, x2, y + 20, main_text,
                      fontSize=10, bold=True, textColor=self.theme.header_fill)
        self.text_box(x1, y + 20, x2, y + 37, sub_text,
                      fontSize=9, textColor="RGB(80,80,80)")

    def content_box(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        title: str = "",
        body_lines: list[str] | None = None,
        fill: str | None = None,
        line: str | None = None,
        title_size: float = 13,
        body_size: float = 9,
        title_color: str = "RGB(30,30,30)",
        body_color: str | None = None,
        roundX: float = 0.05,
        title_pad: float = 10,
        body_line_h: float = 22,
    ) -> None:
        """Add a content box with optional title and multi-line body text.

        The rectangle has no text attribute; title and body are separate
        text_box shapes positioned inside.
        """
        fill = fill or self.theme.box_fill
        line = line or self.theme.box_line
        body_color = body_color or self.theme.body_text

        self.rect(x, y, x + w, y + h,
                  fill=fill, line=line, weight=1.0, roundX=roundX)

        if title:
            self.text_box(
                x + title_pad, y + 8, x + w - title_pad, y + 30,
                title, fontSize=title_size, bold=True, textColor=title_color,
            )

        if body_lines:
            cy = y + 36
            for bl in body_lines:
                self.text_box(
                    x + title_pad, cy, x + w - title_pad, cy + body_line_h,
                    bl, fontSize=body_size, textColor=body_color,
                )
                cy += body_line_h + 4

    def hflow(
        self,
        box_specs: list[dict],
        y: float,
        start_x: float,
        gap: float = 25,
        arrow_weight: float = 1.3,
        mid_h_offset: float | None = None,
    ) -> list[float]:
        """Draw a horizontal row of boxes with arrows between them.

        Each item in *box_specs* is a dict with keys ``w``, ``h``,
        and any kwargs accepted by ``content_box``.

        Returns a list of box x1 positions (useful for alignment).
        """
        positions: list[float] = []
        cx = start_x
        prev_right = None
        for spec in box_specs:
            w = spec["w"]
            h = spec["h"]
            x1 = cx
            # Arrow from previous box
            if prev_right is not None:
                ay = y + (mid_h_offset or h / 2)
                self.line(prev_right + 2, ay, x1 - 2, ay,
                          weight=arrow_weight, arrow="end")
            # Draw the box
            self.content_box(x1, y, w, h, **{k: v for k, v in spec.items() if k not in ("w", "h")})
            positions.append(x1)
            prev_right = x1 + w
            cx = x1 + w + gap + 25  # 25px arrow length
        return positions

    def tag_row(
        self,
        tags: list[str],
        colors: list[str],
        x: float,
        y: float,
        tag_w: float = 58,
        tag_h: float = 26,
        gap: float = 5,
        fontSize: float = 8,
        caption: str = "",
    ) -> None:
        """Draw a horizontal row of coloured tag rectangles."""
        for i, (tag, color) in enumerate(zip(tags, colors)):
            tx = x + i * (tag_w + gap)
            self.rect(
                tx, y, tx + tag_w, y + tag_h,
                text=tag, fill=color, line="RGB(150,150,150)",
                weight=0.5, fontSize=fontSize, roundX=0.04,
            )
        if caption:
            total_w = len(tags) * (tag_w + gap) - gap
            self.text_box(x, y + tag_h + 2, x + total_w, y + tag_h + 16,
                          caption, fontSize=8, textColor="RGB(100,100,100)")

    def feedback_loop(
        self,
        from_y: float,
        to_y: float,
        x_offset: float = 100,
        main_label: str = "",
        sub_label: str = "",
        weight: float = 1.5,
    ) -> None:
        """Draw a dashed feedback polyline from one section to another.

        The polyline goes left from from_y, then up to to_y, then right
        to reconnect.
        """
        fb_x = x_offset
        pts = [
            [fb_x + 40, from_y],
            [fb_x, from_y],
            [fb_x - 15, from_y - 30],
            [fb_x - 15, to_y + 30],
            [fb_x, to_y],
            [160 + 112, to_y],
        ]
        self.polyline(pts, weight=weight, arrow="end", dash=True, noFill=True)

        if main_label:
            mid_y = (from_y + to_y) / 2
            self.text_box(
                fb_x - 80, mid_y - 15, fb_x - 25, mid_y + 5,
                main_label, fontSize=9, bold=True,
                textColor=self.theme.feedback_text,
            )
        if sub_label:
            mid_y = (from_y + to_y) / 2
            self.text_box(
                fb_x - 80, mid_y + 5, fb_x - 25, mid_y + 22,
                sub_label, fontSize=8,
                textColor=self.theme.feedback_sub,
            )

    def formula_chain(
        self,
        terms: list[tuple[str, str, str]],
        x: float,
        y: float,
        box_w: float = 100,
        box_h: float = 26,
        arrow_gap: float = 20,
        fontSize: float = 10,
        operator: str = "=",
    ) -> None:
        """Draw a chain of labelled boxes connected by arrows/operators.

        Each term is (label, fill, line).
        """
        cx = x
        for i, (label, fill, line) in enumerate(terms):
            self.rect(
                cx, y, cx + box_w, y + box_h,
                text=label, fontSize=fontSize, bold=True,
                fill=fill, line=line, weight=0.8, roundX=0.04,
            )
            cx += box_w
            if i < len(terms) - 1:
                # Arrow or operator
                if i == len(terms) - 2 and operator == "=":
                    self.text_box(
                        cx + 3, y + 3, cx + 20, y + 23,
                        "=", fontSize=14, bold=True, textColor="RGB(40,40,40)",
                    )
                    cx += 23
                else:
                    self.line(cx + 2, y + box_h / 2,
                              cx + arrow_gap, y + box_h / 2,
                              weight=1.0, arrow="end")
                    cx += arrow_gap + 3

    # ── Export ───────────────────────────────────────────────────────────

    def to_dict(self, name: str = "Diagram") -> dict:
        """Return the plan as a dict."""
        return {
            "page": {
                "name": name,
                "widthPx": self.width,
                "heightPx": self.height,
                "scalePxPerInch": self.scale,
            },
            "shapes": self.shapes,
        }

    def save(self, path: str | Path, name: str = "Diagram") -> Path:
        """Write the plan to a JSON file with UTF-8 BOM. Returns the path."""
        out = Path(path) if not isinstance(path, Path) else path
        content = json.dumps(self.to_dict(name), ensure_ascii=False, indent=2)
        with open(out, "wb") as f:
            f.write(b"\xef\xbb\xbf" + content.encode("utf-8"))
        print(f"Generated {out.name} with {len(self.shapes)} shapes at {out}")
        print(f"Page: {self.width}x{self.height}px at {self.scale}px/inch")
        return out
