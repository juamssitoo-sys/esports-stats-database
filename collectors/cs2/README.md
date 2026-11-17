# Counter-Strike 2 collector — HLTV

Primary reference: https://www.hltv.org/

HLTV's public site exposes event archives, match results, team/player pages and match-level statistics. The repository records HLTV as the planned CS2 source.

## Collection scope

Historical window: 2025-01-01 through 2026-12-31.

Target entities:
- Events and match series
- Teams, player identities and roster history
- Maps and map scores (including CT/T rounds and overtime when available)
- Per-player map statistics: K/D/A, HS%, ADR, KAST, rating, opening kills/deaths, multi-kills, aces and clutches where published
- Source URL, collection timestamp and raw payload for every imported record

## Important implementation note

This folder is a source specification, not a working HLTV scraper yet. No undocumented endpoint or stable public API is assumed. Before bulk collection, verify current HLTV terms, robots rules, page structure and request limits. Use only permitted access, conservative delays and source attribution. Do not bypass access controls, bot checks or rate limits.

The database migration `database/migrations/002_counter_strike_2.sql` adds CS2-specific per-map statistic fields. The actual parser and backfill job will be added only after a permitted, reproducible data-access method is validated.
