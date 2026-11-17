#!/usr/bin/env python3
"""Build a provisional LoL player master and observed player-team history from ChainCC CSVs.

Usage:
  python scripts/build_lol_player_master.py --input-dir data/raw/chaincc --output-dir data/curated/lol/chaincc
Requires only Python's standard library.
"""
import argparse, csv, hashlib, json, re
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
    print(json.dumps(manifest,indent=2))
if __name__=="__main__": main()
