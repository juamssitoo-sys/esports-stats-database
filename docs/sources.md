# Data sources

| Game | Primary source | Status | Scope |
|---|---|---|---|
| VALORANT | https://www.vlr.gg/ | Adapter scaffold | Matches, maps, player stats |
| Counter-Strike 2 | https://www.hltv.org/ | Reference only; automated scraping prohibited by HLTV Terms §2.2 | Events, matches, maps, player stats; obtain data only through permitted/licensed exports or alternative datasets |
| League of Legends | https://gol.gg/esports/home/ | Primary reference; pending validation | Tournament, game, draft and player statistics |
| League of Legends (secondary) | https://chaincc.lol/free/data/ | Imported successfully; GitHub Actions artifact | 199,830 player-game + 39,966 team-game rows; 2026 is year-to-date; separate provenance |

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

## Counter-Strike 2 — HLTV terms restriction

HLTV Terms of Service (effective 2025-01-27), section 2.2, explicitly prohibits data mining or web scraping of the website/content and commercial exploitation of its content. Therefore this project must not run a scraper against HLTV, use Cloudflare bypasses, or mirror HLTV page data without permission. HLTV remains a manual reference for verification only unless written permission or a licensed data export is obtained. The existing CS2 schema is a target data model, not evidence that HLTV collection is authorized or implemented. See https://www.hltv.org/terms.

For CS2 historical match-level data, evaluate alternative sources whose redistribution rights and 2025–2026 match-level coverage can be verified (for example, properly licensed demo/stat datasets or direct tournament data releases). Do not assume a GitHub repository's code license also licenses its third-party data.

## VALORANT — VLR.gg restriction (blocking)

VLR.gg Terms of Service, last updated 2025-09-16: https://www.vlr.gg/terms

The terms allow properly accessed content for personal, non-commercial use, but separately prohibit automated/non-human access and systematically retrieving data to build or compile a database without VLR's written permission. The non-commercial nature of a university project does **not** waive those separate restrictions.

Therefore VLR.gg can be used as a human-accessed reference within the stated personal/non-commercial scope, but automated collection and a systematic historical database require written permission. Do not run the VLR adapter or bulk backfill before that permission is obtained. The unofficial `axsddlr/vlrggapi` project is a scraper adapter, not an official API; its MIT code licence does not grant rights to VLR content.

The collector now includes an explicit permission confirmation guard, but that flag is an operator attestation, not proof of permission. Do not use it unless written permission has actually been obtained.


## Riot Games Open Access powered by GRID — important restriction

Official announcement: https://lolesports.com/en-US/news/build-with-official-league-of-legends-esports-data  
Access portal and terms: https://grid.gg/riot-open-access/

Riot/GRID Open Access exposes official LoL and VALORANT esports feeds (Central Data Feed and Series State API/Loopfeed). The initial event coverage announced is Worlds 2026; do not infer that it contains the full 2025–2026 historical catalogue.

**This free Open Access tier is not eligible as a data source for FijasPro's betting-oriented use case.** GRID states that Open Access is for non-commercial learning/experimentation and explicitly excludes betting or gambling use. A commercial licence is required for commercial products, subject to GRID approval and pricing. Therefore:
- Do not ingest Open Access data into the FijasPro pipeline or use it to generate betting recommendations.
- It may only be evaluated for a separate non-commercial prototype that complies with its terms.
- For FijasPro, obtain written commercial/betting-use permission and a suitable GRID licence before relying on these feeds.
- The existence of Riot's ordinary developer APIs does not imply access to professional esports historical match feeds or permission for betting use.

For a genuinely non-commercial academic project with no betting/gambling functionality, GRID Open Access is intended for students, researchers and early-stage projects; eligibility, event coverage, delayed-data conditions and the Open Access terms still apply. GRID explicitly excludes any betting or gambling use, even if the project is free and does not earn revenue. If FijasPro includes odds, bookmaker links, wager recommendations, betting picks or other gambling functionality, do not use Open Access data for that functionality without a suitable licence/approval from GRID.

This restriction is separate from the ChainCC CC BY 4.0 dataset; keep each source's licence and provenance independent.
