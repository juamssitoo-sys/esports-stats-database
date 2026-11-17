# Raw and curated data

Do not commit large third-party data files directly to Git unless their license and repository storage policy permit it.

- raw/chaincc/: downloaded ChainCC source archives (CC BY 4.0).
- curated/lol/chaincc/: date-filtered CSVs and a provenance manifest.
- Date scope: 2025-01-01 through 2026-12-31 only.
- Attribution is embedded in the manifest and must accompany redistribution.

Run: python scripts/download_chaincc_lol.py

The downloader requests only the 2025 and 2026 seasons, retains raw compressed archives, filters dates, and writes SHA-256 hashes and row counts. ChainCC is an auxiliary LoL dataset, not a Gol.gg export.
