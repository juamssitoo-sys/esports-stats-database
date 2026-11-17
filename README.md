# Esports Stats Database

Independent public repository for historical esports match data and analytics.

## Scope

- **VALORANT**: primary ingestion source is [VLR.gg](https://www.vlr.gg/).
- **League of Legends** and **Counter-Strike 2**: separate source adapters will be added after the VALORANT pipeline is validated.
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

VLR.gg is a community esports statistics website, not an official Riot Games API. The project can use a compatible self-hosted adapter such as [axsddlr/vlrggapi](https://github.com/axsddlr/vlrggapi), subject to its own license and VLR.gg's terms. Check its current API documentation before running bulk imports.

## Current status

- [x] Public repository initialized
- [x] Historical window defined (2025–2026)
- [x] Initial PostgreSQL schema
- [x] VALORANT ingestion scaffold
- [ ] Verify source adapter against live VLR pages
- [ ] Backfill completed matches from 2025
- [ ] Add League of Legends adapter
- [ ] Add Counter-Strike 2 adapter
- [ ] Analytics API and dashboards

## License

No license has been selected yet. Until one is added, default copyright applies to original code. Source data remains subject to the respective providers' terms and rights.
