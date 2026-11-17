#!/usr/bin/env python3
"""Build a scoped SQLite/CSV release from the public VCT Reference DuckDB snapshot."""
from __future__ import annotations
import argparse, csv, json, sqlite3
from datetime import date, datetime
from pathlib import Path
import duckdb

TABLES = ["matches", "maps", "rounds", "players", "teams", "player_map",
          "kill_matrix", "notables", "stat_source", "feed_fill_meta"]

def qident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'

def sqlite_type(duck_type: str) -> str:
    t = duck_type.upper()
    if any(x in t for x in ("INT", "BOOL")): return "INTEGER"
    if any(x in t for x in ("DOUBLE", "FLOAT", "DECIMAL", "REAL")): return "REAL"
    return "TEXT"

def value(v):
    if isinstance(v, (datetime, date)): return v.isoformat()
    if isinstance(v, (list, dict, tuple)): return json.dumps(v, ensure_ascii=False, default=str)
    return v

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--out", required=True)
    args=ap.parse_args()
    source=Path(args.source); out=Path(args.out); out.mkdir(parents=True, exist_ok=True)
    con=duckdb.connect(str(source), read_only=True)
    start="2025-01-01"; end="2027-01-01"
    match_sql=f"SELECT * FROM matches WHERE utc_timestamp >= TIMESTAMP '{start}' AND utc_timestamp < TIMESTAMP '{end}' AND listing_status = 'Completed' AND is_showmatch = FALSE"
    matches=con.execute(match_sql).fetchdf()
    if matches.empty: raise SystemExit("No completed 2025-2026 VCT matches found")
    match_ids=matches["match_id"].dropna().tolist()
    player_ids=con.execute("SELECT DISTINCT player_id FROM player_map WHERE match_id IN (SELECT match_id FROM matches WHERE utc_timestamp >= ? AND utc_timestamp < ? AND listing_status='Completed' AND is_showmatch=FALSE)", [start,end]).fetchall()
    team_ids=sorted(set(matches["team0_id"].dropna().tolist()+matches["team1_id"].dropna().tolist()))
    filters={
      "matches": match_sql,
      "maps": f"SELECT * FROM maps WHERE match_id IN (SELECT match_id FROM ({match_sql}) scoped_matches)",
      "rounds": f"SELECT * FROM rounds WHERE match_id IN (SELECT match_id FROM ({match_sql}) scoped_matches)",
      "player_map": f"SELECT * FROM player_map WHERE match_id IN (SELECT match_id FROM ({match_sql}) scoped_matches)",
      "kill_matrix": f"SELECT * FROM kill_matrix WHERE match_id IN (SELECT match_id FROM ({match_sql}) scoped_matches)",
      "notables": f"SELECT * FROM notables WHERE match_id IN (SELECT match_id FROM ({match_sql}) scoped_matches)",
      "stat_source": f"SELECT * FROM stat_source WHERE match_id IN (SELECT match_id FROM ({match_sql}) scoped_matches)",
      "players": "SELECT * FROM players WHERE player_id IN (SELECT DISTINCT player_id FROM player_map WHERE match_id IN (SELECT match_id FROM ("+match_sql+") scoped_matches))",
      "teams": "SELECT * FROM teams WHERE team_id IN (SELECT team0_id FROM ("+match_sql+") a UNION SELECT team1_id FROM ("+match_sql+") b)",
      "feed_fill_meta": "SELECT * FROM feed_fill_meta"
    }
    db_path=out/"valorant_vct_2025_2026.sqlite"
    if db_path.exists(): db_path.unlink()
    dst=sqlite3.connect(db_path)
    counts={}
    for table in TABLES:
        desc=con.execute(f"DESCRIBE SELECT * FROM {qident(table)}").fetchall()
        cols=[(r[0],r[1]) for r in desc]
        select_parts=[]
        for name, typ in cols:
            if "[]" in typ or "STRUCT" in typ or "MAP(" in typ:
                select_parts.append(f"CAST({qident(name)} AS VARCHAR) AS {qident(name)}")
            else: select_parts.append(qident(name))
        # Reuse the scoped filter but replace SELECT * with explicit serialization-safe columns.
        query=filters[table]
        query=query.replace("SELECT *", "SELECT "+", ".join(select_parts), 1)
        cur=con.execute(query)
        ddl=", ".join(f"{qident(n)} {sqlite_type(t)}" for n,t in cols)
        dst.execute(f"CREATE TABLE {qident(table)} ({ddl})")
        insert_sql=f"INSERT INTO {qident(table)} VALUES ({','.join('?' for _ in cols)})"
        n=0
        while True:
            batch=cur.fetchmany(5000)
            if not batch: break
            dst.executemany(insert_sql, [[value(v) for v in row] for row in batch])
            n+=len(batch)
        counts[table]=n
        with open(out/f"{table}.csv","w",newline="",encoding="utf-8-sig") as f:
            writer=csv.writer(f); writer.writerow([c[0] for c in cols])
            for row in dst.execute(f"SELECT * FROM {qident(table)}"):
                writer.writerow(row)
    dst.execute("CREATE INDEX idx_maps_match ON maps(match_id)")
    dst.execute("CREATE INDEX idx_player_map_match ON player_map(match_id)")
    dst.execute("CREATE INDEX idx_player_map_player ON player_map(player_id)")
    dst.execute("CREATE INDEX idx_rounds_match ON rounds(match_id)")
    dst.execute("CREATE INDEX idx_kill_matrix_match ON kill_matrix(match_id)")
    dst.commit()
    integrity=dst.execute("PRAGMA integrity_check").fetchone()[0]
    duplicate_matches=dst.execute("SELECT COUNT(*) FROM (SELECT match_id FROM matches GROUP BY match_id HAVING COUNT(*)>1)").fetchone()[0]
    orphan_maps=dst.execute("SELECT COUNT(*) FROM maps x LEFT JOIN matches m USING(match_id) WHERE m.match_id IS NULL").fetchone()[0]
    years=dst.execute("SELECT substr(utc_timestamp,1,4),COUNT(*) FROM matches GROUP BY 1 ORDER BY 1").fetchall()
    coverage=dst.execute("SELECT COUNT(*) total_maps, SUM(CASE WHEN performance_available THEN 1 ELSE 0 END) performance_maps, SUM(CASE WHEN economy_available THEN 1 ELSE 0 END) economy_maps FROM maps").fetchone()
    manifest={
      "dataset":"VALORANT Champions Tour tier-1 historical dataset",
      "source":"VCT Reference","source_url":"https://vct-reference.com/dataset",
      "terms_url":"https://vct-reference.com/terms",
      "attribution":"VCT Reference (vct-reference.com); independent community project, not affiliated with Riot Games.",
      "scope":{"start_date":start,"end_date_inclusive":"2026-12-31","match_filter":"Completed, non-showmatch, UTC timestamp in 2025-2026"},
      "source_snapshot_bytes":source.stat().st_size,
      "sqlite_file":db_path.name,"rows":counts,
      "year_match_counts":[{"year":y,"matches":n} for y,n in years],
      "map_stat_coverage":{"total_maps":coverage[0],"performance_available_maps":coverage[1],"economy_available_maps":coverage[2]},
      "quality":{"sqlite_integrity_check":integrity,"duplicate_match_ids":duplicate_matches,"orphan_maps":orphan_maps},
      "limitations":["Only tier-1 VCT matches and qualifying regional events included by source methodology; not all amateur/open events.","Some optional stat blocks are missing, especially China domestic league; consult maps.performance_available and maps.economy_available before interpreting absent values.","Player/team identity fields reflect source identifiers and names; no additional identity resolution performed.","2026 is year-to-date as of source snapshot, not a complete year."],
      "generated_utc":datetime.utcnow().isoformat(timespec="seconds")+"Z"
    }
    with open(out/"valorant_manifest.json","w",encoding="utf-8") as f: json.dump(manifest,f,ensure_ascii=False,indent=2)
    with open(out/"README.txt","w",encoding="utf-8") as f:
        f.write("VALORANT VCT 2025-2026 curated dataset\n\n")
        f.write("Source: VCT Reference — https://vct-reference.com/dataset\nTerms: https://vct-reference.com/terms\nAttribution: VCT Reference (vct-reference.com)\n\n")
        f.write("SQLite contains one table per source table, scoped to completed non-showmatch VCT matches dated 2025-01-01 through 2026-12-31 UTC. CSV files mirror those tables.\n\n")
        f.write("IMPORTANT: missing optional stat blocks are not zero. Use maps.performance_available and maps.economy_available to gate analyses.\n\n")
        f.write(json.dumps(manifest,ensure_ascii=False,indent=2))
    dst.close(); con.close()
    if integrity!="ok" or duplicate_matches or orphan_maps: raise SystemExit("Quality checks failed")
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
