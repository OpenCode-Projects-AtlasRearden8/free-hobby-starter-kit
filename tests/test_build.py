"""Tests for the Free Hobby Starter Kit build.

Every sheet in sources/ must build a valid, print-ready Letter-size PDF.
Run with:  python3 -m unittest discover tests -v
"""

import unittest
import tempfile
from pathlib import Path

from pypdf import PdfReader

from build import build_sheet

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources"

# The kit's full intended contents: every hobby sheet and how many
# printed pages it should produce at Letter size.
EXPECTED_SHEETS = {
    "birdwatching": 3,
    "stargazing": 3,
    "sketching": 3,
    "hiking": 3,
    "boardgames": 3,
    "letterwriting": 4,
}

PAGE_WIDTH_PT = 612.0   # US Letter, portrait
PAGE_HEIGHT_PT = 792.0


class BuiltKit:
    """Builds every sheet once into a temp dir, shared by all tests."""

    pdfs: dict[str, Path] = {}
    readers: dict[str, PdfReader] = {}


class BuildAllSheets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        BuiltKit.tmp = tempfile.TemporaryDirectory()
        out_dir = Path(BuiltKit.tmp.name)
        for name, expected_pages in EXPECTED_SHEETS.items():
            html = SOURCES / f"{name}.html"
            if not html.exists():
                continue
            pdf = build_sheet(html, out_dir)
            BuiltKit.pdfs[name] = pdf
            BuiltKit.readers[name] = PdfReader(str(pdf))

    @classmethod
    def tearDownClass(cls):
        BuiltKit.tmp.cleanup()

    def test_every_expected_sheet_exists_as_html(self):
        for name in EXPECTED_SHEETS:
            self.assertTrue(
                (SOURCES / f"{name}.html").exists(),
                f"missing HTML source for {name}",
            )

    def test_every_sheet_built_a_pdf(self):
        for name in EXPECTED_SHEETS:
            self.assertIn(name, BuiltKit.pdfs, f"{name} did not build a PDF")

    def test_pdf_files_are_real_pdfs(self):
        for name, path in BuiltKit.pdfs.items():
            head = path.read_bytes()[:8]
            self.assertTrue(
                head.startswith(b"%PDF"),
                f"{name}.pdf does not start with %PDF header: {head!r}",
            )

    def test_every_sheet_has_expected_page_count(self):
        for name, expected_pages in EXPECTED_SHEETS.items():
            reader = BuiltKit.readers[name]
            self.assertEqual(
                len(reader.pages),
                expected_pages,
                f"{name}: expected {expected_pages} pages, got {len(reader.pages)}",
            )

    def test_every_page_is_letter_portrait(self):
        for name, reader in BuiltKit.readers.items():
            for i, page in enumerate(reader.pages):
                w = float(page.mediabox.width)
                h = float(page.mediabox.height)
                self.assertAlmostEqual(w, PAGE_WIDTH_PT, delta=1.0,
                                       msg=f"{name} page {i+1} width")
                self.assertAlmostEqual(h, PAGE_HEIGHT_PT, delta=1.0,
                                       msg=f"{name} page {i+1} height")

    def test_no_page_is_blank(self):
        for name, reader in BuiltKit.readers.items():
            for i, page in enumerate(reader.pages):
                text = (page.extract_text() or "").strip()
                self.assertTrue(
                    text,
                    f"{name} page {i+1} extracted no text (likely blank)",
                )

    def test_intro_page_names_its_hobby(self):
        titles = {
            "birdwatching": "Bird-Watching",
            "stargazing": "Stargazing Night",
            "sketching": "Sketching",
            "hiking": "Hiking",
            "boardgames": "Board Games We Own",
            "letterwriting": "Letter-Writing Kit",
        }
        for name, title in titles.items():
            first_page = BuiltKit.readers[name].pages[0].extract_text()
            self.assertIn(title, first_page,
                          f"{name} intro page does not mention '{title}'")


if __name__ == "__main__":
    unittest.main()
