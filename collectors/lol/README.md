# League of Legends collector — source specification

**Primary source:** [Games of Legends (Gol.gg)](https://gol.gg/esports/home/)

Gol.gg presents competitive League of Legends statistics and links to recent games, tournament pages, match lists, and tournament/player/team/champion statistics.

## Historical scope

- Start: 2025-01-01
- End: 2026-12-31
- Competitions: professional matches discoverable on Gol.gg during this window.

## Collection targets

1. Tournament metadata and source URL.
2. Individual game identity, match/tournament association, date, patch, duration, side and result.
3. Team-level results and objectives: kills, gold, towers, dragons by type, barons, first blood and first tower.
4. Player-game statistics: champion, role, K/D/A, CS, gold, damage and vision metrics where published.
5. Draft picks and bans.
6. Objective/event timeline only if the page exposes a reliable structured record.

## Implementation status

**Specification only — no live ingestion is implemented or validated yet.** The public site is the selected source, but no official Gol.gg API has been verified. Do not build against an assumed API or undocumented endpoint. First inspect representative tournament, match and player pages and determine which fields are actually present in the public HTML.

## Responsible access

- Review current terms of use and robots rules before collection.
- Use conservative request pacing and identify the collector appropriately.
- Do not bypass login, subscription, CAPTCHA, anti-bot or other technical controls.
- Do not claim access to premium analyst/betting features unless separately authorized.
- Save immutable raw captures with URL, fetched timestamp, payload hash and parser version.
- Keep missing values NULL; never fabricate or infer match statistics.
- Make ingestion idempotent using stable source identifiers and unique constraints.

## Analysis requirements

For any Over/Under or frequency calculation, expose the exact population and sample size (for example, player-game observations or team-games). Do not mix series-level and individual-game denominators. Record whether the statistic is a per-game count, rate, percentage or cumulative total.
