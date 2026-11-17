#!/usr/bin/env python3
"""Build a provisional LoL player master and observed player-team history from ChainCC CSVs.

Usage:
  python scripts/build_lol_player_master.py --input-dir data/raw/chaincc --output-dir data/curated/lol/chaincc
Requires only Python's standard library.
"""
import argparse, csv, hashlib, json, re, sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

def norm(value):
    return re.sub(r"\\s+", " ", (value or "").strip()).casefold()

def parse_date(value):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=timezone.utc) if "+" not in value and "Z" not in value else datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


def build_sqlite(out, manifest):
    db_path = out / "lol_player_master_2025_2026.sqlite"
    if db_path.exists():
        db_path.unlink()
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys=ON")
    con.executescript("""
      CREATE TABLE source_registry(source TEXT PRIMARY KEY, source_url TEXT NOT NULL, license TEXT NOT NULL, attribution TEXT NOT NULL);
      CREATE TABLE players(
        player_id TEXT PRIMARY KEY, game TEXT NOT NULL, source TEXT NOT NULL REFERENCES source_registry(source),
        source_player_id TEXT, source_identity_key TEXT NOT NULL UNIQUE, handle TEXT NOT NULL, aliases TEXT,
        real_name TEXT, country TEXT, first_seen_utc TEXT, last_seen_utc TEXT,
        games_observed INTEGER NOT NULL, teams_observed INTEGER NOT NULL, team_names TEXT,
        roles_observed TEXT, leagues_observed TEXT, identity_status TEXT NOT NULL,
        identity_warning TEXT, source_url TEXT NOT NULL, license TEXT NOT NULL
      );
      CREATE TABLE player_team_observations(
        observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_source_identity_key TEXT NOT NULL REFERENCES players(source_identity_key),
        player_handle_observed TEXT NOT NULL, team_name_observed TEXT NOT NULL,
        first_game_seen_utc TEXT, last_game_seen_utc TEXT, games_with_team INTEGER NOT NULL,
        roles_observed TEXT, source TEXT NOT NULL REFERENCES source_registry(source),
        source_url TEXT NOT NULL, license TEXT NOT NULL, interval_semantics TEXT NOT NULL,
        UNIQUE(player_source_identity_key, team_name_observed)
      );
      CREATE TABLE dataset_metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL);
      CREATE INDEX idx_players_handle ON players(handle);
      CREATE INDEX idx_team_obs_player ON player_team_observations(player_source_identity_key);
      CREATE INDEX idx_team_obs_team ON player_team_observations(team_name_observed);
    """)
    con.execute("INSERT INTO source_registry VALUES (?,?,?,?)", (
        "ChainCC", manifest["source_url"], manifest["license"], manifest["attribution"]))
    with (out / "players_master_2025_2026.csv").open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            row["games_observed"] = int(row["games_observed"] or 0)
            row["teams_observed"] = int(row["teams_observed"] or 0)
            cols = list(row)
            con.execute(f"INSERT INTO players ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)})", [row[k] for k in cols])
    with (out / "player_team_observations_2025_2026.csv").open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            row["games_with_team"] = int(row["games_with_team"] or 0)
            cols = list(row)
            con.execute(f"INSERT INTO player_team_observations ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)})", [row[k] for k in cols])
    for key, value in manifest.items():
        con.execute("INSERT INTO dataset_metadata VALUES (?,?)", (key, json.dumps(value, ensure_ascii=False)))
    con.commit()
    integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
    player_count = con.execute("SELECT COUNT(*) FROM players").fetchone()[0]
    observation_count = con.execute("SELECT COUNT(*) FROM player_team_observations").fetchone()[0]
    orphan_count = con.execute("""SELECT COUNT(*) FROM player_team_observations o LEFT JOIN players p
                                  ON p.source_identity_key=o.player_source_identity_key WHERE p.player_id IS NULL""").fetchone()[0]
    con.close()
    if integrity != "ok" or player_count != manifest["unique_source_handle_keys"] or observation_count != manifest["player_team_observation_rows"] or orphan_count:
        raise RuntimeError(f"SQLite validation failed: integrity={integrity}, players={player_count}, observations={observation_count}, orphans={orphan_count}")
    print(f"SQLite validated: {player_count} provisional players, {observation_count} player-team observations")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-dir",default="data/raw/chaincc")
    ap.add_argument("--output-dir",default="data/curated/lol/chaincc")
    args=ap.parse_args()
    inp=Path(args.input_dir); out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)
    players=defaultdict(lambda: {"names":set(),"teams":set(),"roles":set(),"leagues":set(),"dates":[],"games":set()})
    affiliations=defaultdict(lambda: {"names":set(),"teams":set(),"roles":set(),"dates":[],"games":set()})
    total=0
    for year in (2025,2026):
        path=inp/f"chaincc-players-{year}.csv"
        if not path.exists():
            raise SystemExit(f"Missing input CSV: {path}")
        with path.open(encoding="utf-8-sig",newline="") as f:
            for row in csv.DictReader(f):
                dt=parse_date(row.get("date",""))
                if not dt or not (datetime(2025,1,1,tzinfo=timezone.utc) <= dt < datetime(2027,1,1,tzinfo=timezone.utc)):
                    continue
                handle=(row.get("playername") or "").strip()
                key=norm(handle)
                if not key: continue
                team=(row.get("team_name") or "").strip()
                role=(row.get("position") or "").strip()
                league=(row.get("league") or "").strip()
                game=(row.get("game_id") or "").strip()
                p=players[key]; p["names"].add(handle); p["teams"].add(team); p["roles"].add(role); p["leagues"].add(league); p["dates"].append(dt); p["games"].add(game)
                a=affiliations[(key,norm(team))]; a["names"].add(handle); a["teams"].add(team); a["roles"].add(role); a["dates"].append(dt); a["games"].add(game)
                total+=1
    def join(values): return " | ".join(sorted(x for x in values if x))
    player_fields=["player_id","game","source","source_player_id","source_identity_key","handle","aliases","real_name","country","first_seen_utc","last_seen_utc","games_observed","teams_observed","team_names","roles_observed","leagues_observed","identity_status","identity_warning","source_url","license"]
    with (out/"players_master_2025_2026.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=player_fields); w.writeheader()
        for key,g in sorted(players.items()):
            names=sorted(g["names"]); pid="chaincc_lol_"+hashlib.sha256(key.encode()).hexdigest()[:16]
            w.writerow(dict(player_id=pid,game="LOL",source="ChainCC",source_player_id="",source_identity_key="chaincc_lol_handle:"+key,handle=names[0],aliases=join(names[1:]),real_name="",country="",first_seen_utc=min(g["dates"]).isoformat(),last_seen_utc=max(g["dates"]).isoformat(),games_observed=len(g["games"]),teams_observed=len(g["teams"]- {""}),team_names=join(g["teams"]),roles_observed=join(g["roles"]),leagues_observed=join(g["leagues"]),identity_status="PROVISIONAL_HANDLE_ONLY",identity_warning="ChainCC CSV has no stable player ID; same-handle players may collide. Never merge across sources by handle alone.",source_url="https://chaincc.lol/free/data/",license="CC BY 4.0; attribution required"))
    aff_fields=["player_source_identity_key","player_handle_observed","team_name_observed","first_game_seen_utc","last_game_seen_utc","games_with_team","roles_observed","source","source_url","license","interval_semantics"]
    with (out/"player_team_observations_2025_2026.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=aff_fields); w.writeheader()
        for (key,_),g in sorted(affiliations.items()):
            w.writerow(dict(player_source_identity_key="chaincc_lol_handle:"+key,player_handle_observed=join(g["names"]),team_name_observed=join(g["teams"]),first_game_seen_utc=min(g["dates"]).isoformat(),last_game_seen_utc=max(g["dates"]).isoformat(),games_with_team=len(g["games"]),roles_observed=join(g["roles"]),source="ChainCC",source_url="https://chaincc.lol/free/data/",license="CC BY 4.0; attribution required",interval_semantics="Observed match range only; not an authoritative roster contract interval"))
    manifest={"source":"ChainCC Open Dataset","source_url":"https://chaincc.lol/free/data/","license":"CC BY 4.0","attribution":"Data source: ChainCC (https://chaincc.lol/free/data/), licensed under CC BY 4.0.","window_utc":["2025-01-01","2026-12-31"],"source_rows_after_date_filter":total,"unique_source_handle_keys":len(players),"player_team_observation_rows":len(affiliations),"identity_limitations":"The source CSV has no stable player ID, real name or country. IDs are deterministic project keys based on normalized display handles and remain provisional; homonymous players may collide. Team dates are observed match dates, not official roster intervals.","generated_utc":datetime.now(timezone.utc).isoformat()}
    (out/"players_master_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    build_sqlite(out, manifest)
    print(json.dumps(manifest,indent=2))
if __name__=="__main__": main()
