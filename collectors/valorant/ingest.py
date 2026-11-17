"""Conservative raw-data ingester for a self-hosted VLR-compatible API.

This first stage stores source payloads immutably. Normalization into match/map/player
tables is deliberately separate so provider schema changes cannot silently corrupt
the analytical tables.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import httpx
import psycopg
from dotenv import load_dotenv

SOURCE_SLUG = "vlr-gg"
PARSER_VERSION = "0.1.0"
GAME_SLUG = "valorant"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest VALORANT match data from a VLR-compatible API.")
    parser.add_argument("--from", dest="date_from", type=date.fromisoformat, required=True)
    parser.add_argument("--to", dest="date_to", type=date.fromisoformat, required=True)
    parser.add_argument("--max-pages", type=int, default=1, help="Maximum results pages to request.")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and validate without database writes.")
    return parser.parse_args()


def request_json(client: httpx.Client, url: str, params: dict[str, Any] | None = None) -> Any:
    response = client.get(url, params=params)
    response.raise_for_status()
    return response.json()


def unwrap(payload: Any) -> Any:
    if isinstance(payload, dict):
        data = payload.get("data")
        if data is not None:
            return data
    return payload


def extract_segments(payload: Any) -> list[dict[str, Any]]:
    data = unwrap(payload)
    if isinstance(data, dict):
        for key in ("segments", "matches", "results"):
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    raise ValueError("Unrecognized results payload: expected data.segments / data.matches / data.results")


def get_source_ids(conn: psycopg.Connection) -> tuple[int, int]:
    row = conn.execute("SELECT id FROM sources WHERE slug=%s", (SOURCE_SLUG,)).fetchone()
    game = conn.execute("SELECT id FROM games WHERE slug=%s", (GAME_SLUG,)).fetchone()
    if not row or not game:
        raise RuntimeError("Apply database/schema.sql before ingestion.")
    return row[0], game[0]


def store_payload(conn: psycopg.Connection, source_id: int, game_id: int,
                  entity_type: str, entity_id: str | None, source_url: str | None,
                  payload: dict[str, Any]) -> None:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    conn.execute(
        """INSERT INTO source_payloads
           (source_id, game_id, entity_type, source_entity_id, source_url, payload_hash, payload, parser_version)
           VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb,%s)
           ON CONFLICT (source_id, entity_type, source_entity_id, payload_hash) DO NOTHING""",
        (source_id, game_id, entity_type, entity_id, source_url, digest, canonical, PARSER_VERSION),
    )


def main() -> None:
    load_dotenv()
    args = parse_args()
    if args.date_to < args.date_from:
        raise SystemExit("--to must be on or after --from")
    base = os.getenv("VLR_API_BASE_URL", "").rstrip("/")
    if not base:
        raise SystemExit("Set VLR_API_BASE_URL in .env to your self-hosted VLR-compatible API.")
    timeout = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
    delay = float(os.getenv("REQUEST_DELAY_SECONDS", "1.5"))
    user_agent = os.getenv("USER_AGENT", "EsportsStatsDatabase/0.1")
    db_url = os.getenv("DATABASE_URL")
    if not args.dry_run and not db_url:
        raise SystemExit("Set DATABASE_URL in .env, or use --dry-run.")

    headers = {"User-Agent": user_agent, "Accept": "application/json"}
    count = 0
    conn_context = psycopg.connect(db_url) if (db_url and not args.dry_run) else None
    try:
        with httpx.Client(timeout=timeout, headers=headers, follow_redirects=True) as client:
            for page in range(1, args.max_pages + 1):
                # axsddlr/vlrggapi documents /v2/match?q=results with page controls.
                url = f"{base}/v2/match"
                payload = request_json(client, url, params={
                    "q": "results", "from_page": page, "to_page": page,
                    "num_pages": 1, "request_delay": delay,
                })
                matches = extract_segments(payload)
                if not matches:
                    break
                for match in matches:
                    match_date = match.get("date") or match.get("unix_timestamp")
                    # Keep records with unknown dates for audit; filter only parseable dates.
                    parsed_date = None
                    if isinstance(match_date, str):
                        for fmt in ("%Y/%m/%d", "%Y-%m-%d"):
                            try:
                                parsed_date = datetime.strptime(match_date[:10], fmt).date()
                                break
                            except ValueError:
                                pass
                    if parsed_date and not (args.date_from <= parsed_date <= args.date_to):
                        continue
                    source_id = str(match.get("id") or match.get("match_id") or "") or None
                    source_url = match.get("url") or match.get("match_page")
                    if args.dry_run:
                        print(json.dumps({"source_id": source_id, "date": match_date, "url": source_url}, ensure_ascii=False))
                    else:
                        assert conn_context is not None
                        _, game_id = get_source_ids(conn_context)
                        store_payload(conn_context, 1, game_id, "match_result", source_id, source_url, match)
                    count += 1
                if not args.dry_run and conn_context:
                    conn_context.commit()
                time.sleep(delay)
    finally:
        if conn_context:
            conn_context.close()
    print(f"Processed {count} result records for {args.date_from} through {args.date_to}.")


if __name__ == "__main__":
    main()
