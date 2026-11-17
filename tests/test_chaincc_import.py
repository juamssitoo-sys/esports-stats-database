import gzip
import tempfile
import unittest
from pathlib import Path

from scripts.download_chaincc_lol import filter_csv, parse_day


class ChainCCImportTests(unittest.TestCase):
    def test_date_parsing(self):
        self.assertEqual(parse_day("2026-11-17 12:30:00"), "2026-11-17")
        self.assertEqual(parse_day("17/11/2025"), "2025-11-17")

    def test_filters_window_and_preserves_columns(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "source.csv.gz"
            output = root / "filtered.csv"
            with gzip.open(archive, "wt", encoding="utf-8", newline="") as f:
                f.write("date,game_id,team,extra\n")
                f.write("2024-12-31,g0,Old,keep\n")
                f.write("2025-01-01,g1,Blue,yes\n")
                f.write("2026-12-31,g2,Red,yes\n")
                f.write("bad-date,g3,Unknown,no\n")
            counts = filter_csv(archive, output)
            self.assertEqual(counts, {"accepted": 2, "rejected_bad_date": 1, "outside_window": 1})
            text = output.read_text(encoding="utf-8")
            self.assertIn("extra", text)
            self.assertNotIn("g0", text)


if __name__ == "__main__":
    unittest.main()
