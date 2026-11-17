import csv
import tempfile
import unittest
from pathlib import Path

from collectors.lol.csv_import import normalize_headers, parse_date, process


class GolCsvImportTests(unittest.TestCase):
    def test_header_aliases(self):
        self.assertEqual(normalize_headers(["Game Date", "Team Name", "K"]),
                         {"Game Date": "date", "Team Name": "team", "K": "kills"})

    def test_date_formats(self):
        self.assertEqual(parse_date("17/11/2026"), "2026-11-17")

    def test_window_and_raw_preservation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "input.csv"
            output = root / "out.jsonl"
            with source.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=["Date", "Tournament", "Team", "Kills", "Unknown field"])
                w.writeheader()
                w.writerow({"Date":"2026-05-01","Tournament":"Test Cup","Team":"Blue","Kills":"12","Unknown field":"keep me"})
                w.writerow({"Date":"2024-12-31","Tournament":"Old Cup","Team":"Red","Kills":"9"})
            stats = process(source, output, "https://gol.gg/example/")
            self.assertEqual(stats, {"accepted":1,"rejected":0,"outside_window":1})
            payload = output.read_text(encoding="utf-8")
            self.assertIn("keep me", payload)
            self.assertIn('"kills": 12', payload)


if __name__ == "__main__":
    unittest.main()
