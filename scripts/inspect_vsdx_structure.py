#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path


PAGE_RE = re.compile(r"visio/pages/page\d+\.xml$")


def inspect(path: Path) -> dict:
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        pages = [name for name in names if PAGE_RE.match(name)]
        media = [name for name in names if name.startswith("visio/media/")]
        text_nodes = 0
        shape_tags = 0
        reference_marker = False
        for page in pages:
            xml = zf.read(page).decode("utf-8", "ignore")
            text_nodes += xml.count("<Text>")
            shape_tags += xml.count("<Shape ")
            if "Original_Image_Reference" in xml:
                reference_marker = True
        return {
            "file": str(path.resolve()),
            "pages": len(pages),
            "media_files": len(media),
            "shape_tags": shape_tags,
            "text_nodes": text_nodes,
            "reference_page_marker": reference_marker,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a VSDX for modular editable diagram structure.")
    parser.add_argument("vsdx", type=Path)
    parser.add_argument("--expect-single-page", action="store_true")
    parser.add_argument("--min-media", type=int, default=None)
    parser.add_argument("--min-text", type=int, default=None)
    parser.add_argument("--forbid-reference", action="store_true")
    args = parser.parse_args()

    info = inspect(args.vsdx)
    print(json.dumps(info, ensure_ascii=False, indent=2))

    failures = []
    if args.expect_single_page and info["pages"] != 1:
        failures.append(f"expected 1 page, found {info['pages']}")
    if args.min_media is not None and info["media_files"] < args.min_media:
        failures.append(f"expected at least {args.min_media} media files, found {info['media_files']}")
    if args.min_text is not None and info["text_nodes"] < args.min_text:
        failures.append(f"expected at least {args.min_text} text nodes, found {info['text_nodes']}")
    if args.forbid_reference and info["reference_page_marker"]:
        failures.append("found Original_Image_Reference marker")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

