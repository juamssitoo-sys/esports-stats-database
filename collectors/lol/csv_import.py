"""Validate and normalize a user-supplied Gol.gg CSV export.

This intentionally does not crawl Gol.gg. Use only exports/files that you are
permitted to collect. Original rows are preserved in a JSONL sidecar so that
unmapped source fields are not silently discarded.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

START = "2025-01-01"
END = "2026-12-31"
ALIASES = {
    "date": {"date", "game date", "match date"},
    "tournament": {"tournament", "competition"},
    "team": {"team", "team name"},
    "opponent": {"opponent", "enemy team"},
    "champion": {"champion", "pick"},
    "player": {"player", "summoner", "player name"},
    "kills": {"kills", "k"},
    "deaths": {"deaths", "d"},
    "assists": {"assists", "a"},
    "cs": {"cs", "minions", "creep score"},
    "gold": {"gold", "total gold"},
    "duration": {"duration", "game duration", "length"},
}
REQUIRED = {"date", "tournament", "team"}


def key(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", " ").split())


def normalize_headers(headers: list[str]) -> dict[str, str]:
    reverse = {alias: canonical for canonical, aliases in ALIASES.items() for alias in aliases}
    return {h: reverse[key(h)] for h in headers if key(h) in reverse}


def parse_date(value: str) -> str:
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass
    raise ValueError(f"Unsupported date format: {value!r}")


def clean_value(value: str) -> Any:
    value = value.strip()
    if value == "":
        return None
    return value


def convert_row(row: dict[str, str], headers: dict[str, str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for original, canonical in headers.items():
        value = clean_value(row.get(original, ""))
        if canonical == "date" and value is not None:
            value = parse_date(value)
        elif canonical in {"kills", "deaths", "assists", "cs", "gold"} and value is not None:
            try:
                value = int(value.replace(",", ""))
            except ValueError:
                raise ValueError(f"Expected integer for {canonical}: {value!r}")
        out[canonical] = value
    return out


def process(input_path: Path, output_path: Path, source_url: str) -> dict[str, int]:
    raw_bytes = input_path.read_bytes()
    digest = hashlib.sha256(raw_bytes).hexdigest()
    fetched_at = datetime.now(timezone.utc).isoformat()
    accepted = rejected = outside_window = 0

    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV has no header row")
        headers = normalize_headers(reader.fieldnames)
        missing = REQUIRED - set(headers.values())
        if missing:
            raise ValueError("Missing required columns after mapping: " + ", ".join(sorted(missing)))

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as out:
            for line_no, row in enumerate(reader, start=2):
                try:
                    normalized = convert_row(row, headers)
                    if not START <= normalized["date"] <= END:
                        outside_window += 1
                        continue
                    record = {
                        "source": "gol-gg",
                        "source_url": source_url,
                        "retrieved_at": fetched_at,
                        "input_sha256": digest,
                        "input_line": line_no,
                        "parser_version": "0.1.0",
                        "normalized": normalized,
                        "raw": row,
                    }
                    out.write(json.dumps(record, ensure_ascii=False) + "\n")
                    accepted += 1
                except (ValueError, TypeError):
                    rejected += 1
    return {"accepted": accepted, "rejected": rejected, "outside_window": outside_window}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path, help="Permitted Gol.gg CSV export")
    parser.add_argument("--output", type=Path, default=Path("data/raw/golgg-games.jsonl"))
    parser.add_argument("--source-url", default="https://gol.gg/esports/home/")
    args = parser.parse_args()
    print(json.dumps(process(args.csv, args.output, args.source_url), indent=2))


if __name__ == "__main__":
    main()
