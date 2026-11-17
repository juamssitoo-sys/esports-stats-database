# Esports Stats Database

Independent public repository for historical esports match data and analytics.

## Scope

- **VALORANT**: primary discovery source is [VLR.gg](https://www.vlr.gg/); an unofficial adapter is being evaluated. Riot/GRID Open Access may be suitable for a non-commercial academic project, but excludes betting/gambling use.
- **League of Legends**: ChainCC CC BY 4.0 2025–2026 player-game and team-game CSVs are imported as a secondary source; Gol.gg remains the intended primary reference. Riot/GRID Open Access is available to students/researchers for non-commercial experimentation. Eligibility depends on actual functionality: bookmaker odds/lines, wager-oriented picks or bet-placement links may count as betting/gambling use and are excluded even for free academic projects.
- **Counter-Strike 2**: HLTV is a reference source only. HLTV Terms §2.2 prohibits scraping; obtain permission/licensed data or use a separately licensed alternative dataset.
- Historical window: **2025-01-01 through 2026-12-31** (inclusive).

## Data principles

1. Preserve source payloads and source URLs for traceability.
2. Normalize matches, maps, teams, players and per-map player statistics.
3. Never fabricate missing statistics. A missing field remains NULL / unavailable.
4. Make ingestion idempotent using source IDs and unique constraints.
5. Respect source terms, robots rules, rate limits and reasonable request delays. Do not bypass access controls or anti-bot protections.
6. Record collection timestamps and parser versions.

## Repository layout

```text
database/schema.sql       PostgreSQL schema
collectors/valorant/      VALORANT ingestion client
config/                   Example configuration
data/raw/                 Local raw payloads (ignored by Git)
docs/                     Source and data dictionary notes
```

## Quick start

Requirements: Python 3.11+, PostgreSQL 15+ and access to a self-hosted VLR-compatible API.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Create a database and apply the schema:

```bash
psql "$DATABASE_URL" -f database/schema.sql
```

Copy `.env.example` to `.env` and set the database URL and VLR API base URL. Never commit credentials.

Run a small test first:

```bash
python -m collectors.valorant.ingest --from 2025-01-01 --to 2026-12-31 --max-pages 1 --dry-run
```

Then remove `--dry-run` to persist the raw source payloads. The collector intentionally requires an explicitly configured API endpoint; it does not assume VLR.gg operates an official public API.

## Source notes

VLR.gg is a community esports statistics website, not an official Riot Games API. The project can use a compatible self-hosted adapter such as [axsddlr/vlrggapi](https://github.com/axsddlr/vlrggapi), subject to VLR.gg's written permission. Do not run automated collection or bulk imports without written permission covering the intended commercial use.

## Current status

- [x] Public repository initialized
- [x] Historical window defined (2025–2026)
- [x] Initial PostgreSQL schema
- [x] VALORANT ingestion scaffold
- [ ] Obtain VLR.gg written permission for automated collection and FijasPro commercial/betting use before any VALORANT backfill
- [x] Import ChainCC LoL 2025–2026 CSV artifact (secondary source; not yet loaded into PostgreSQL)
- [ ] Validate Gol.gg access and reconcile LoL match records
- [ ] Confirm FijasPro has no betting/gambling functionality before using GRID Open Access; if it does, Open Access is excluded regardless of non-commercial status
- [ ] Identify a licensed CS2 2025–2026 match-level dataset; do not scrape HLTV
- [ ] Analytics API and dashboards

## License

No license has been selected yet. Until one is added, default copyright applies to original code. Source data remains subject to the respective providers' terms and rights.
