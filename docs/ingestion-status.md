# Ingestion status — 2025–2026

Last successful run: 2026-11-17 05:48 UTC  
Workflow: https://github.com/juamssitoo-sys/esports-stats-database/actions/runs/44026633208  
Artifact: https://github.com/juamssitoo-sys/esports-stats-database/actions/runs/44026633208/artifacts/14302629642  
Artifact name: chaincc-lol-2025-2026  
Artifact size: 52,890,031 bytes  
Retention: 90 days (expires 2027-02-15)

## Imported auxiliary LoL dataset (ChainCC, CC BY 4.0)

| Season | Player-game rows | Team-game rows | Bad dates rejected | Out-of-window rows |
|---|---:|---:|---:|---:|
| 2025 | 100,530 | 20,106 | 0 | 0 |
| 2026 (year-to-date at source update) | 99,300 | 19,860 | 0 | 0 |
| **Total** | **199,830** | **39,966** | **0** | **0** |

The four original gzipped CSVs and four date-filtered CSVs plus manifest were uploaded as a GitHub Actions artifact. The dataset page reports its latest update as 2026-11-16; 2026 is therefore year-to-date, not a complete future calendar year.

This dataset is an attributed secondary source, not Gol.gg data. Its own source label and CC BY 4.0 attribution must remain attached to any redistribution. It is not yet loaded into PostgreSQL or merged with Gol.gg records.

## Primary-source collection status

| Primary source | Status |
|---|---|
| VLR.gg (VALORANT) | **Blocked for FijasPro use pending written permission**: current Terms prohibit automated collection/database compilation and commercial exploitation without permission; collector now has an explicit permission guard |
| HLTV (CS2) | Source-specific collection and permitted access still to be validated |
| Gol.gg (LoL) | Source-specific export/access still to be validated |

No HLTV or VLR scrape has been run. We explicitly excluded a third-party HLTV scraper whose README says it bypasses Cloudflare. We also rejected season-level player aggregates that lack per-match identifiers for match-level prop analysis.

## Next data quality gates

1. Inspect the ChainCC artifact's CSV columns and reconcile player/team rows on game_id + side.
2. Validate the 2025–2026 LoL records against Gol.gg where possible; keep both source versions separate.
3. Build date-scoped, stable-ID match ingestors for VLR and HLTV only after access and rate limits are confirmed.
4. Maintain dated roster history and aliases; never collapse teams or players by display name alone.


## Newly verified licensing blockers (2026-11-17)

- VLR.gg Terms (updated 2025-09-16) prohibit automated/non-human access, scraping/data mining, systematic database compilation without written permission, and commercial exploitation without express prior written permission. No VLR automated collection has been run. The VALORANT collector now stops unless the operator explicitly attests to written permission; this flag is not a substitute for obtaining that permission.
- Riot/GRID Open Access is intended for students, academics, hobbyists and early-stage non-commercial projects. The user describes FijasPro as a free university project with esports analysis, statistics and forecasts, no sponsor and only contextual mentions of bookmaker names. Mere name mentions do not establish gambling functionality; bookmaker odds/lines, wager-oriented picks or bet-placement links may be excluded. Confirm actual functionality and intended use with GRID before registering or ingesting its feed.
- ChainCC CC BY 4.0 remains the only imported LoL source currently eligible for commercial reuse subject to attribution and the licence conditions. It remains in a GitHub Actions artifact, not PostgreSQL.
- Consequently, the immediate next step for VALORANT is to secure VLR written permission for automated historical database collection, or identify a source whose licence permits it. For official Riot/GRID feeds, first confirm that the project's actual functionality is not betting/gambling; a non-commercial academic analytics project may qualify for Open Access.
