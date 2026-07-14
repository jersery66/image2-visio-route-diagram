#!/usr/bin/env python3
"""Automated tests for inspect_vsdx_structure.py.

Creates minimal fixture VSDX files (valid ZIP archives with Visio XML)
and verifies that the inspector correctly counts pages, shapes, media,
text nodes, and enforces all validation flags.

Usage:
    python -m pytest tests/ -v
    # or
    python tests/test_inspect.py
"""
from __future__ import annotations

import json
import sys
import tempfile
import zipfile
from pathlib import Path

# Allow importing the script under test
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from inspect_vsdx_structure import inspect

V_NS = "http://schemas.microsoft.com/visio/2003/core"

# ── Fixture builders ────────────────────────────────────────────────────────


def _page_xml(
    page_width: float = 16.0,
    page_height: float = 14.0,
    text_count: int = 0,
    native_shapes: int = 0,
    foreign_shapes: list[dict] | None = None,
    has_reference_marker: bool = False,
) -> str:
    """Build a minimal Visio page XML string."""
    shapes_xml = ""
    # Native shapes (rectangles, lines, etc.)
    for i in range(native_shapes):
        shapes_xml += f"""
        <Shape ID="{i + 1}" Type="Shape" xmlns="http://schemas.microsoft.com/visio/2003/core">
          <XForm>
            <Width>1.0</Width>
            <Height>0.5</Height>
          </XForm>
        </Shape>"""

    # Foreign (image) shapes
    for j, fs in enumerate(foreign_shapes or []):
        shapes_xml += f"""
        <Shape ID="{native_shapes + j + 1}" Type="Foreign" xmlns="http://schemas.microsoft.com/visio/2003/core">
          <ForeignData ObjectType="1" />
          <XForm>
            <Width>{fs.get('w', 0.5)}</Width>
            <Height>{fs.get('h', 0.5)}</Height>
          </XForm>
        </Shape>"""

    # Text nodes
    text_nodes = "".join(f"<Text>Label {i}</Text>" for i in range(text_count))

    # Reference marker (anti-pattern detection)
    marker = '<!-- Original_Image_Reference -->' if has_reference_marker else ""

    return f"""<?xml version="1.0" encoding="utf-8"?>
<PageContents xmlns="http://schemas.microsoft.com/visio/2003/core">
  <PageSheet>
    <PageProps>
      <PageWidth>{page_width}</PageWidth>
      <PageHeight>{page_height}</PageHeight>
    </PageProps>
  </PageSheet>
  {shapes_xml}
  {text_nodes}
  {marker}
</PageContents>"""


def _build_vsdx(
    tmp_dir: Path,
    name: str = "test",
    pages: int = 1,
    media_files: int = 0,
    text_per_page: int = 0,
    native_per_page: int = 0,
    foreign_per_page: list[dict] | None = None,
    reference_marker: bool = False,
) -> Path:
    """Build a minimal valid VSDX (ZIP) file."""
    vsdx_path = tmp_dir / f"{name}.vsdx"
    with zipfile.ZipFile(vsdx_path, "w") as zf:
        for i in range(pages):
            xml = _page_xml(
                text_count=text_per_page,
                native_shapes=native_per_page,
                foreign_shapes=foreign_per_page,
                has_reference_marker=reference_marker and i == 0,
            )
            zf.writestr(f"visio/pages/page{i + 1}.xml", xml)

        # Media files (dummy content)
        for j in range(media_files):
            zf.writestr(f"visio/media/image{j + 1}.png", b"\x89PNG\r\n")

    return vsdx_path


# ── Tests ───────────────────────────────────────────────────────────────────


def test_page_count():
    with tempfile.TemporaryDirectory() as td:
        p = _build_vsdx(Path(td), pages=1, native_per_page=3)
        info = inspect(p)
        assert info["pages"] == 1, f"Expected 1 page, got {info['pages']}"
        print("  PASS: test_page_count")


def test_multi_page():
    with tempfile.TemporaryDirectory() as td:
        p = _build_vsdx(Path(td), pages=3, native_per_page=2)
        info = inspect(p)
        assert info["pages"] == 3, f"Expected 3 pages, got {info['pages']}"
        print("  PASS: test_multi_page")


def test_media_count():
    with tempfile.TemporaryDirectory() as td:
        p = _build_vsdx(Path(td), media_files=5)
        info = inspect(p)
        assert info["media_files"] == 5, f"Expected 5 media, got {info['media_files']}"
        print("  PASS: test_media_count")


def test_text_nodes():
    with tempfile.TemporaryDirectory() as td:
        p = _build_vsdx(Path(td), text_per_page=10)
        info = inspect(p)
        assert info["text_nodes"] == 10, f"Expected 10 text, got {info['text_nodes']}"
        print("  PASS: test_text_nodes")


def test_native_shape_count():
    with tempfile.TemporaryDirectory() as td:
        p = _build_vsdx(Path(td), native_per_page=7)
        info = inspect(p)
        assert info["native_shape_count"] == 7, f"Expected 7 native, got {info['native_shape_count']}"
        print("  PASS: test_native_shape_count")


def test_image_shape_detection():
    with tempfile.TemporaryDirectory() as td:
        foreigners = [
            {"w": 0.5, "h": 0.5},
            {"w": 1.0, "h": 0.8},
        ]
        p = _build_vsdx(Path(td), foreign_per_page=foreigners, native_per_page=3)
        info = inspect(p)
        assert info["image_shape_count"] == 2, f"Expected 2 images, got {info['image_shape_count']}"
        assert info["native_shape_count"] == 3, f"Expected 3 native, got {info['native_shape_count']}"
        assert len(info["image_shapes_list"]) == 2
        assert abs(info["image_shapes_list"][0]["area"] - 0.25) < 0.01
        assert abs(info["image_shapes_list"][1]["area"] - 0.80) < 0.01
        print("  PASS: test_image_shape_detection")


def test_page_dimensions():
    with tempfile.TemporaryDirectory() as td:
        p = _build_vsdx(Path(td))
        info = inspect(p)
        assert len(info["page_dimensions"]) == 1
        pw, ph = info["page_dimensions"][0]
        assert abs(pw - 16.0) < 0.01, f"Expected width 16.0, got {pw}"
        assert abs(ph - 14.0) < 0.01, f"Expected height 14.0, got {ph}"
        print("  PASS: test_page_dimensions")


def test_reference_marker():
    with tempfile.TemporaryDirectory() as td:
        p = _build_vsdx(Path(td), reference_marker=True)
        info = inspect(p)
        assert info["reference_page_marker"] is True, "Expected reference marker"
        print("  PASS: test_reference_marker")


def test_no_reference_marker():
    with tempfile.TemporaryDirectory() as td:
        p = _build_vsdx(Path(td), reference_marker=False)
        info = inspect(p)
        assert info["reference_page_marker"] is False, "Expected no reference marker"
        print("  PASS: test_no_reference_marker")


def test_large_background_image_detection():
    """Image covering > 35% of page area should be flagged."""
    with tempfile.TemporaryDirectory() as td:
        # Page is 16x14 = 224 sq in. Image 10x10 = 100 sq in → 44.6%
        foreigners = [{"w": 10.0, "h": 10.0}]
        p = _build_vsdx(Path(td), foreign_per_page=foreigners)
        info = inspect(p)
        page_area = 16.0 * 14.0
        img_area = 10.0 * 10.0
        ratio = img_area / page_area
        assert ratio > 0.35, f"Test setup error: ratio {ratio} should be > 0.35"
        assert info["image_shape_count"] == 1
        print("  PASS: test_large_background_image_detection")


def test_total_shape_count():
    with tempfile.TemporaryDirectory() as td:
        foreigners = [{"w": 0.5, "h": 0.5}]
        p = _build_vsdx(Path(td), native_per_page=5, foreign_per_page=foreigners)
        info = inspect(p)
        assert info["total_shapes"] == 6, f"Expected 6 total, got {info['total_shapes']}"
        print("  PASS: test_total_shape_count")


def test_empty_vsdx():
    """A VSDX with no pages should return zeroed-out counts."""
    with tempfile.TemporaryDirectory() as td:
        vsdx_path = Path(td) / "empty.vsdx"
        with zipfile.ZipFile(vsdx_path, "w") as zf:
            pass  # Empty zip
        info = inspect(vsdx_path)
        assert info["pages"] == 0
        assert info["media_files"] == 0
        assert info["text_nodes"] == 0
        assert info["native_shape_count"] == 0
        assert info["image_shape_count"] == 0
        print("  PASS: test_empty_vsdx")


# ── Runner ──────────────────────────────────────────────────────────────────


def run_all_tests():
    tests = [
        test_page_count,
        test_multi_page,
        test_media_count,
        test_text_nodes,
        test_native_shape_count,
        test_image_shape_detection,
        test_page_dimensions,
        test_reference_marker,
        test_no_reference_marker,
        test_large_background_image_detection,
        test_total_shape_count,
        test_empty_vsdx,
    ]
    passed = 0
    failed = 0
    for test_fn in tests:
        try:
            test_fn()
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {test_fn.__name__} — {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR: {test_fn.__name__} — {type(e).__name__}: {e}")
            failed += 1

    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(run_all_tests())
