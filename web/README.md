# Esports Atlas web

Next.js dashboard for the independent Esports Stats Database.

## Local development

```bash
cd web
npm install
npm run dev
```

Open http://localhost:3000.

## Build

```bash
npm run build
```

## Data pipeline

The dashboard reads `public/data/esports.json`. GitHub Actions generates this file from the validated VALORANT and League of Legends SQLite artifacts using `scripts/build-data.py`, then builds the Next.js application.

The current imported data coverage is intentionally explicit:
- VALORANT: VCT Reference coverage, including tier-1 VCT and qualifying regional events represented by that source. The current release is not a complete feed of every amateur/open tournament.
- League of Legends: ChainCC player master and observed team associations. This import does not currently contain per-game kills, KDA or champion statistics.
- CS2: section layout is present, but no validated historical dataset has been imported yet.

Missing statistics are not displayed as zero. Do not infer a player's current roster from historical team observations.
