"""Download ChainCC's CC BY 4.0 LoL 2025–2026 CSVs and filter by date.

Auxiliary data source, not Gol.gg data. Preserve attribution and raw archives.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://chaincc.lol/data"
SEASONS = (2025, 2026)
KINDS = ("players", "teams")
START, END = "2025-01-01", "2026-12-31"
ATTRIBUTION = "ChainCC, LoL esports match dataset, https://chaincc.lol/free/data/ (CC BY 4.0; accessed 2026-11-17)"


def parse_day(value: str) -> str:
    value = (value or "").strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value[:19], fmt).date().isoformat()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date value: {value!r}")


def download(url: str, destination: Path) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "EsportsStatsDatabase/0.1 (research; attribution ChainCC)"})
    digest = hashlib.sha256()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(request, timeout=60) as response, destination.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
            out.write(chunk)
    return digest.hexdigest()


def filter_csv(archive: Path, output: Path) -> dict:
    with gzip.open(archive, "rt", encoding="utf-8-sig", newline="") as src:
        reader = csv.DictReader(src)
        if not reader.fieldnames:
            raise ValueError(f"No CSV headers in {archive}")
        date_col = next((h for h in reader.fieldnames if h.strip().lower() in {"date", "game_date", "gamedate"}), None)
        if not date_col:
            raise ValueError(f"No recognized date column in {archive}: {reader.fieldnames}")
        output.parent.mkdir(parents=True, exist_ok=True)
        accepted = rejected = outside = 0
        with output.open("w", encoding="utf-8", newline="") as dst:
            writer = csv.DictWriter(dst, fieldnames=reader.fieldnames)
            writer.writeheader()
            for row in reader:
                try:
                    day = parse_day(row.get(date_col, ""))
                    if not START <= day <= END:
                        outside += 1
                        continue
                    writer.writerow(row)
                    accepted += 1
                except ValueError:
                    rejected += 1
    return {"accepted": accepted, "rejected_bad_date": rejected, "outside_window": outside}


def main() -> None:
    root = Path("data")
    raw_dir = root / "raw" / "chaincc"
    curated_dir = root / "curated" / "lol" / "chaincc"
    manifest = {
        "source": "ChainCC",
        "source_url": "https://chaincc.lol/free/data/",
        "license": "CC BY 4.0",
        "attribution": ATTRIBUTION,
        "date_window": [START, END],
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "files": [],
    }
    for year in SEASONS:
        for kind in KINDS:
            name = f"chaincc-{kind}-{year}.csv.gz"
            url = f"{BASE}/{name}"
            archive = raw_dir / name
            sha = download(url, archive)
            output = curated_dir / f"chaincc-{kind}-{year}.csv"
            counts = filter_csv(archive, output)
            manifest["files"].append({
                "url": url,
                "raw_file": str(archive),
                "raw_sha256": sha,
                "filtered_file": str(output),
                "season": year,
                "entity": kind,
                **counts,
            })
    (curated_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
