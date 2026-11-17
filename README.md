# Esports Stats Database

Independent historical esports data project. This repository is not connected to FijasPro.

## Scope

- **VALORANT**: tier-1 VCT matches and qualifying regional events, with match, map, round, player, team, per-player-map statistics, kill matchups and notable events.
- **League of Legends**: ChainCC 2025–2026 player-game data normalized into a provisional player master.
- **Counter-Strike 2**: planned for a later phase.
- Historical window: **2025-01-01 through 2026-12-31** (inclusive). 2026 data is year-to-date through the latest source snapshot.

## Current releases

### VALORANT

Source: [VCT Reference dataset](https://vct-reference.com/dataset). Terms: [VCT Reference Terms of Service](https://vct-reference.com/terms).

A public DuckDB snapshot is downloaded by GitHub Actions, scoped to completed non-showmatch VCT matches from 2025 and 2026, and exported as SQLite plus CSV files. Attribution: VCT Reference (vct-reference.com). The source is an independent community project and is not affiliated with Riot Games.

Latest verified release (2026-11-17):
- 1,120 series (498 in 2025; 622 in 2026 YTD)
- 2,860 maps and 60,587 rounds
- 28,600 player-map rows
- 484 players and 67 teams
- 67,850 kill-matrix rows and 106,957 notable events
- SQLite integrity check: `ok`; no duplicate match IDs; no orphan maps

**Coverage limitations:** this dataset focuses on tier-1 VCT and qualifying events, not every open/amateur tournament. Optional performance/economy stat blocks are incomplete on some maps, especially China domestic league. Missing values are not zero; analyses must gate on `maps.performance_available` and `maps.economy_available`.

### League of Legends

Source: [ChainCC Open Dataset](https://chaincc.lol/free/data/), CC BY 4.0; attribution required.

Latest validated player master:
- 4,082 provisional handle-based player identity records
- 7,011 player-team observations
- Stable source-native player IDs are unavailable in this dataset; records may not correspond one-to-one with real people.

## Combined SQLite release

The combined release keeps source-specific schemas separate using table prefixes:
- `valorant_*`: VCT Reference tables.
- `lol_*`: ChainCC LoL player-master tables.
- `master_metadata`: scope, sources and caveats.

The SQLite file is generated as a release artifact and can be downloaded from the project’s latest successful GitHub Actions run.

## Reproducibility

- VALORANT acquisition and build: `.github/workflows/acquire-valorant-vct-reference.yml`
- VALORANT builder: `scripts/build_valorant_sqlite.py`
- LoL builder: `scripts/build_lol_player_master.py`

## Data principles

1. Preserve source attribution and record the source URL.
2. Never fabricate missing statistics; missing values remain NULL/unavailable.
3. Preserve source IDs and source-specific schemas.
4. Record coverage limitations and collection timestamps.
5. Respect each provider's terms and do not bypass access controls or anti-bot protections.

## License

Original repository code and imported datasets have separate rights. Source data remains subject to the terms and licenses of its respective providers. No blanket license is granted for third-party data by this repository.
