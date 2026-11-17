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
| VLR.gg (VALORANT) | Repository/API adapter identified; self-hosting and source access validation still required |
| HLTV (CS2) | Source-specific collection and permitted access still to be validated |
| Gol.gg (LoL) | Source-specific export/access still to be validated |

No HLTV or VLR scrape has been run. We explicitly excluded a third-party HLTV scraper whose README says it bypasses Cloudflare. We also rejected season-level player aggregates that lack per-match identifiers for match-level prop analysis.

## Next data quality gates

1. Inspect the ChainCC artifact's CSV columns and reconcile player/team rows on game_id + side.
2. Validate the 2025–2026 LoL records against Gol.gg where possible; keep both source versions separate.
3. Build date-scoped, stable-ID match ingestors for VLR and HLTV only after access and rate limits are confirmed.
4. Maintain dated roster history and aliases; never collapse teams or players by display name alone.
