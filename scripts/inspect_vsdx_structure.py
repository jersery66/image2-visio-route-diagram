#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


PAGE_RE = re.compile(r"visio/pages/page\d+\.xml$")
V_NS = "http://schemas.microsoft.com/visio/2003/core"


def _float(text: str | None, default: float = 0.0) -> float:
    try:
        return float(text) if text else default
    except (ValueError, TypeError):
        return default


def inspect(path: Path) -> dict:
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        pages = [name for name in names if PAGE_RE.match(name)]
        media = [name for name in names if name.startswith("visio/media/")]
        text_nodes = 0
        reference_marker = False
        page_dimensions: list[tuple[float, float]] = []
        image_shapes: list[dict] = []
        native_shape_count = 0
        total_shape_count = 0

        for page in pages:
            xml_content = zf.read(page).decode("utf-8", "ignore")
            text_nodes += xml_content.count("<Text>")
            if "Original_Image_Reference" in xml_content:
                reference_marker = True

            # Parse XML for page dimensions and detailed shape classification
            try:
                root = ET.fromstring(xml_content)
            except ET.ParseError:
                continue

            # --- Page dimensions ---
            for page_sheet in root.iter(f"{{{V_NS}}}PageSheet"):
                for page_props in page_sheet.iter(f"{{{V_NS}}}PageProps"):
                    pw_el = page_props.find(f"{{{V_NS}}}PageWidth")
                    ph_el = page_props.find(f"{{{V_NS}}}PageHeight")
                    pw = _float(pw_el.text if pw_el is not None else None)
                    ph = _float(ph_el.text if ph_el is not None else None)
                    page_dimensions.append((pw, ph))

            # --- Shape classification ---
            for shape in root.iter(f"{{{V_NS}}}Shape"):
                total_shape_count += 1
                fd = shape.find(f"{{{V_NS}}}ForeignData")
                if fd is not None:
                    xform = shape.find(f"{{{V_NS}}}XForm")
                    if xform is not None:
                        w_el = xform.find(f"{{{V_NS}}}Width")
                        h_el = xform.find(f"{{{V_NS}}}Height")
                        w = _float(w_el.text if w_el is not None else None)
                        h = _float(h_el.text if h_el is not None else None)
                        if w > 0 and h > 0:
                            image_shapes.append(
                                {"width": w, "height": h, "area": w * h}
                            )
                else:
                    native_shape_count += 1

        return {
            "file": str(path.resolve()),
            "pages": len(pages),
            "media_files": len(media),
            "total_shapes": total_shape_count,
            "image_shapes_list": image_shapes,
            "image_shape_count": len(image_shapes),
            "native_shape_count": native_shape_count,
            "text_nodes": text_nodes,
            "reference_page_marker": reference_marker,
            "page_dimensions": page_dimensions,
        }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect a VSDX for modular editable diagram structure."
    )
    parser.add_argument("vsdx", type=Path)
    parser.add_argument("--expect-single-page", action="store_true")
    parser.add_argument("--min-media", type=int, default=None)
    parser.add_argument("--min-text", type=int, default=None)
    parser.add_argument("--min-image-shapes", type=int, default=None,
                        help="Expected minimum number of image shapes on the page.")
    parser.add_argument("--min-native-shapes", type=int, default=None,
                        help="Expected minimum number of native (non-image) Visio shapes.")
    parser.add_argument("--forbid-reference", action="store_true")
    parser.add_argument(
        "--forbid-large-background-image",
        action="store_true",
        help="Fail if any single image occupies more than --max-image-area-ratio "
        "of the page area.",
    )
    parser.add_argument(
        "--max-image-area-ratio",
        type=float,
        default=0.35,
        help="Maximum allowed image-to-page area ratio (default: 0.35).",
    )
    args = parser.parse_args()

    info = inspect(args.vsdx)
    print(json.dumps(info, ensure_ascii=False, indent=2))

    failures = []
    if args.expect_single_page and info["pages"] != 1:
        failures.append(f"expected 1 page, found {info['pages']}")
    if args.min_media is not None and info["media_files"] < args.min_media:
        failures.append(
            f"expected at least {args.min_media} media files, "
            f"found {info['media_files']}"
        )
    if args.min_text is not None and info["text_nodes"] < args.min_text:
        failures.append(
            f"expected at least {args.min_text} text nodes, "
            f"found {info['text_nodes']}"
        )
    if args.min_image_shapes is not None and info["image_shape_count"] < args.min_image_shapes:
        failures.append(
            f"expected at least {args.min_image_shapes} image shapes on page, "
            f"found {info['image_shape_count']}"
        )
    if args.min_native_shapes is not None and info["native_shape_count"] < args.min_native_shapes:
        failures.append(
            f"expected at least {args.min_native_shapes} native Visio shapes, "
            f"found {info['native_shape_count']}"
        )
    if args.forbid_reference and info["reference_page_marker"]:
        failures.append("found Original_Image_Reference marker")

    if args.forbid_large_background_image:
        max_ratio = args.max_image_area_ratio
        if info["page_dimensions"] and info["image_shapes_list"]:
            pw, ph = info["page_dimensions"][0]
            page_area = pw * ph
            if page_area > 0:
                for img in info["image_shapes_list"]:
                    ratio = img["area"] / page_area
                    if ratio > max_ratio:
                        failures.append(
                            f"image shape {img['width']:.1f}x{img['height']:.1f} "
                            f"occupies {ratio:.1%} of page area "
                            f"({max_ratio:.0%} max allowed)"
                        )
            elif info["image_shapes_list"]:
                failures.append(
                    "could not determine page dimensions to check image area ratio"
                )

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
