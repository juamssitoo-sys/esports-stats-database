# Data dictionary and coverage

## VALORANT

| Entity | Grain | Important fields |
|---|---|---|
| Match | One series | source match ID, event, date, status, best-of, team scores |
| Match map | One map in a series | map name, map order, round scores, winner |
| Player match stats | One player on one map | K/D/A, ACS, ADR, KAST, HS%, first kills/deaths |
| Round | One round on one map | round number, attacking side, winner, round type |
| Kill event | One kill event | killer, victim, assister, weapon, first-blood flag |

Some metrics are not available for every match, event, or historical season. NULL means unavailable or not supplied by the source; it must not be interpreted as zero.

## Frequency calculations

Frequencies should be calculated from the actual number of eligible observations:
- Over threshold rate = count(observations above threshold) / count(non-null observations).
- First Blood rate = first kills / eligible maps (or rounds, with the denominator explicitly stated).
- Map win rate = map wins / maps played.

Always expose the sample size and date range beside a percentage. Do not mix series-level and map-level denominators.

## Planned cross-game extensions

League of Legends and Counter-Strike 2 will use game-specific statistic tables or typed JSON extensions. Do not force game-specific metrics into VALORANT columns.
