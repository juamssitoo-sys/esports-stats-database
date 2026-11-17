# League of Legends collector — Gol.gg CSV ingestion

**Source:** [Games of Legends (Gol.gg)](https://gol.gg/esports/home/)

## Current status

- Gol.gg's homepage identifies it as a home for competitive League of Legends statistics.
- Automated crawling is **not enabled**. The site's current robots.txt and terms could not be reliably verified in this pass, so this project does not send automated requests to match pages.
- The importer accepts a CSV export that the operator is permitted to obtain. It preserves every original row alongside normalized fields and provenance metadata.
- This is a staging/import step, not a completed historical backfill or database loader.

## Date scope

Only records dated 2025-01-01 through 2026-12-31 are written. Rows outside the window are counted and skipped.

## Run

```bash
python -m collectors.lol.csv_import path/to/golgg-export.csv \
  --output data/raw/golgg-games.jsonl \
  --source-url "https://gol.gg/esports/home/"
```

The importer reports accepted, rejected and out-of-window rows. It records the input SHA-256, retrieval timestamp, source URL, parser version and original CSV row. Unknown source columns remain in the raw row. Missing values remain null; numeric fields are not guessed.

## Supported initial CSV columns

Header aliases are deliberately conservative: date, tournament, team, opponent, player, champion, kills, deaths, assists, CS, gold and duration. Add aliases only after inspecting a real export. The importer does not claim to normalize every Gol.gg page or all available metrics.

## Tests

```bash
python -m unittest discover -s tests
```

## Next validation gate

Obtain a permitted representative CSV export and compare normalized records against the corresponding Gol.gg match page. Only then expand the field mapping and implement database upserts. Do not bypass login, subscription, CAPTCHA, robots rules or technical restrictions.
