# External dataset and repository audit (2025–2026)

Audit date: 2026-11-17. A public repository does not automatically grant permission to redistribute third-party data.

## Scope and identity rules
- Include records dated 2025-01-01 through 2026-12-31 only.
- Preserve source-native team/player IDs and names as observed on each match date.
- Do not overwrite historical team names with current names. Keep dated aliases and roster intervals.
- A player transfer does not create a new player identity when a stable source ID exists.
- Never use 2024 records to fill gaps in the production 2025–2026 dataset.

## Primary sources selected by the project owner

| Game | Primary source | Intended records | Collection status |
|---|---|---|---|
| VALORANT | https://www.vlr.gg/ | Matches, maps, rounds, player/map stats, events, roster history | Self-hosted API adapter must be validated; no historical backfill yet |
| CS2 | https://www.hltv.org/ | Matches, maps, player/map stats, events, rosters | Canonical reference; no automated collector/backfill yet |
| League of Legends | https://gol.gg/esports/home/ | Tournaments, games, drafts, team/player statistics | Primary reference; no verified official API or completed export |

## Additional public datasets and code reviewed

### VALORANT — axsddlr/vlrggapi
- Repository: https://github.com/axsddlr/vlrggapi
- Repository code license: MIT.
- Unofficial self-hostable REST API for VLR pages: match results/details, per-map K/D/A/ACS/rating, round logs, player/team/event pages and roster transactions.
- Its README warns that the hosted Vercel instance is down; self-hosting is the documented route.
- Use as an adapter/code reference only. VLR content remains subject to VLR terms and access rules. Validate date coverage and rate limits before backfill.

### CS2 — Aokua/csgopred
- Repository: https://github.com/Aokua/csgopred
- README reports 68,523 deduplicated matches from 2015-11 through 2026-10, 56,730 maps, and a raw player-statistics CSV via Git LFS.
- Combines several origins (HLTV, community dataset, Kaggle and Liquipedia) and normalizes team names. Useful as a cross-check, not a replacement for HLTV provenance.
- Code is MIT; README says the snapshot is CC BY 4.0 but third-party source data remains subject to its own terms. Do not mirror third-party data until each component's redistribution rights are verified.
- Candidate for a 2025–2026 comparison once its snapshot is lawfully obtained and inspected.

### CS2 — EiJee/HLTV2025Dashboard
- Repository: https://github.com/EiJee/HLTV2025Dashboard
- Contains a small player_stats.csv and dashboard for the first half of 2025.
- The inspected CSV is a player aggregate without per-match date/game keys; unsuitable for match-level Over/Under frequencies or roster timelines. Reference only.

### CS2 — StrandedPond/hltv_scraper
- Repository: https://github.com/StrandedPond/hltv_scraper
- Contains player/team CSV snapshots and an automated HLTV scraper.
- Its README explicitly describes bypassing Cloudflare. We will NOT reuse that bypass behavior or run its scraper. Inspected aggregates do not establish 2025–2026 per-match provenance, so they are not accepted as canonical data.

### League of Legends — ChainCC Open Dataset
- Dataset page: https://chaincc.lol/free/data/
- Publishes 2025 and 2026 gzipped CSVs: player-game rows and team-game rows.
- Reported counts: 2025 has 100,530 player rows and 20,106 team rows; 2026 has 99,300 player rows and 19,860 team rows (page updated 2026-11-16).
- Coverage includes date, league, split, patch, teams, champion/pick, player stats, team draft and objectives.
- Dataset page states CC BY 4.0; reuse requires attribution. Strong secondary LoL dataset/schema cross-check; it is not Gol.gg data and must retain its own source label.

### League of Legends — Oracle's Elixir mirror
- Repository candidate: https://github.com/twodotone/lolproj/tree/main/Data/csv
- Inspected directory contains a 2026 Oracle's Elixir CSV (~11.4 MB); no corresponding 2025 file was present in that directory listing.
- Obtain 2025 and 2026 files from the canonical publisher when possible and retain attribution/licensing. Do not assume this mirror is complete.

## Rejected shortcuts
- No guessed undocumented APIs.
- No Cloudflare/CAPTCHA/login/subscription bypass.
- No mixing aggregate player totals with match-level rows.
- No merging entities by display name alone when source IDs or dated aliases are available.
- No 2024 records in production analytical tables.

## Current ingestion status
Code and schema are prepared, but this audit has not imported live match rows. The ChainCC downloader is a reproducible auxiliary ingestion step; VLR, HLTV and Gol.gg still need source-specific access validation and date-complete collection. Every calculated rate must expose sample size and unit (series, map, game, player-game or round).
