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
from datetime import date, datetime
from typing import Any

import httpx
import psycopg
from dotenv import load_dotenv

SOURCE_SLUG = "vlr-gg"
PARSER_VERSION = "0.2.0"
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



def parse_match_date(match: dict[str, Any]) -> date | None:
    """Parse VLR list dates without silently dropping human-readable dates."""
    candidates = (match.get("date"), match.get("unix_timestamp"), match.get("date_time"))
    formats = ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S", "%B %d, %Y", "%b %d, %Y")
    for candidate in candidates:
        if not isinstance(candidate, str) or not candidate.strip():
            continue
        value = candidate.strip()
        for fmt in formats:
            try:
                return datetime.strptime(value[:19], fmt).date()
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except ValueError:
            pass
    return None


def extract_detail(payload: Any) -> dict[str, Any]:
    data = unwrap(payload)
    if isinstance(data, dict):
        segments = data.get("segments")
        if isinstance(segments, list) and segments and isinstance(segments[0], dict):
            return segments[0]
        return data
    raise ValueError("Unrecognized match detail payload")


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
    delay = float(os.getenv("REQUEST_DELAY_SECONDS", "3.2"))
    user_agent = os.getenv("USER_AGENT", "EsportsStatsDatabase/0.1")
    db_url = os.getenv("DATABASE_URL")
    if not args.dry_run and not db_url:
        raise SystemExit("Set DATABASE_URL in .env, or use --dry-run.")

    headers = {"User-Agent": user_agent, "Accept": "application/json"}
    count = 0
    conn_context = psycopg.connect(db_url) if (db_url and not args.dry_run) else None
    source_db_id = game_db_id = None
    if conn_context:
        source_db_id, game_db_id = get_source_ids(conn_context)
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
                    parsed_date = parse_match_date(match)
                    if parsed_date is None or not (args.date_from <= parsed_date <= args.date_to):
                        continue
                    source_id = str(match.get("id") or match.get("match_id") or "") or None
                    source_url = match.get("url") or match.get("match_page")
                    if not source_id:
                        continue
                    detail_url = f"{base}/v2/match/{source_id}/details"
                    detail_payload = request_json(client, detail_url, params={"include": "event,date,status,teams,maps,performance,economy"})
                    detail = extract_detail(detail_payload)
                    if args.dry_run:
                        print(json.dumps({"source_id": source_id, "date": parsed_date.isoformat(),
                                          "url": source_url, "maps": len(detail.get("maps", []))}, ensure_ascii=False))
                    else:
                        assert conn_context is not None
                        assert source_db_id is not None and game_db_id is not None
                        store_payload(conn_context, source_db_id, game_db_id, "match_result", source_id, source_url, match)
                        store_payload(conn_context, source_db_id, game_db_id, "match_details", source_id, detail_url, detail)
                    count += 1
                    time.sleep(delay)
                if not args.dry_run and conn_context:
                    conn_context.commit()
                time.sleep(delay)
    finally:
        if conn_context:
            conn_context.close()
    print(f"Processed {count} result records for {args.date_from} through {args.date_to}.")


if __name__ == "__main__":
    main()
