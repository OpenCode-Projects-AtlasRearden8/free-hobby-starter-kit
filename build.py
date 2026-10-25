#!/usr/bin/env python3
"""Build script for the Free Hobby Starter Kit.

Converts every HTML sheet in sources/ into a print-ready PDF in printables/.
Local build only: no network, no accounts, no API keys.

Usage:
    python3 build.py                 # build every sheet
    python3 build.py --sheet birdwatching
    python3 build.py --sources DIR --out DIR
"""

import argparse
import sys
from pathlib import Path

try:
    from weasyprint import HTML
except ImportError:
    sys.exit("weasyprint is missing. Install it with: pip install weasyprint")


def build_sheet(html_path: Path, out_dir: Path) -> Path:
    pdf_path = out_dir / (html_path.stem + ".pdf")
    doc = HTML(filename=str(html_path)).render()
    doc.write_pdf(str(pdf_path))
    print(f"  built {pdf_path.name} ({len(doc.pages)} pages)")
    return pdf_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build printable hobby sheets.")
    default_sources = Path(__file__).resolve().parent / "sources"
    default_out = Path(__file__).resolve().parent / "printables"
    parser.add_argument("--sources", type=Path, default=default_sources)
    parser.add_argument("--out", type=Path, default=default_out)
    parser.add_argument("--sheet", help="build one sheet, e.g. birdwatching")
    args = parser.parse_args()

    sources = sorted(p for p in args.sources.glob("*.html"))
    if not sources:
        sys.exit(f"No HTML sheets found in {args.sources}")

    if args.sheet:
        sources = [p for p in sources if p.stem == args.sheet]
        if not sources:
            sys.exit(f"Unknown sheet: {args.sheet}")

    args.out.mkdir(parents=True, exist_ok=True)

    print(f"Building {len(sources)} sheet(s) into {args.out}/")
    built = [build_sheet(p, args.out) for p in sources]
    print(f"Done: {len(built)} PDF(s) ready to print.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
