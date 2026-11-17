# Data sources

| Game | Primary source | Status | Scope |
|---|---|---|---|
| VALORANT | https://www.vlr.gg/ | Adapter scaffold | Matches, maps, player stats |
| Counter-Strike 2 | https://www.hltv.org/ | Source specification added | Events, matches, maps, player stats |
| League of Legends | https://gol.gg/esports/home/ | Primary reference; pending validation | Tournament, game, draft and player statistics |
| League of Legends (secondary) | https://chaincc.lol/free/data/ | CC BY 4.0 dataset + downloader | Player-game and team-game CSVs for 2025–2026; separate provenance |

## League of Legends — Games of Legends (Gol.gg)

Gol.gg describes itself as a database of competitive League of Legends statistics. Its public pages expose recent games, tournament match lists, tournament-level statistics, and player/team/champion statistics. The home page and tournament-stat pages are useful discovery and verification surfaces.

Target collection window: 2025-01-01 through 2026-12-31.

Target fields, where published and verifiable:
- Game/match identity, tournament, date, patch, duration, blue/red side and result.
- Team kills, deaths, gold, towers, dragons by type, barons, first blood and first tower.
- Player/champion: kills, deaths, assists, CS, gold, damage, vision and role/position metrics where available.
- Draft: picks and bans by side.
- Objective/event details only when the source exposes them at sufficient granularity.

Important: this is a source specification, not a working collector. No official Gol.gg API has been verified. Do not assume one exists. Before automated collection, inspect the current terms, robots rules, page structure and request limits; do not bypass access controls. Store raw captures, source URLs, retrieval timestamps and parser versions. Missing values remain NULL.

Gol.gg also offers some premium analyst/betting features; do not assume those fields are available in the public pages or accessible without the relevant subscription.

## Provenance and responsible collection

- Retain source URLs and retrieval timestamps.
- Preserve raw payloads and parser versions.
- Check each provider's current terms, robots rules and request limits before collection.
- Do not assume an official API exists where none has been documented.
- Do not circumvent authentication, CAPTCHAs, anti-bot controls or technical restrictions.
- Missing values remain NULL and all calculated rates show their sample size.
