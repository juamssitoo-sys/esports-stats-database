#!/usr/bin/env python3
import argparse, collections, json, re, sqlite3
from pathlib import Path

def rows(conn, sql, args=()):
    conn.row_factory=sqlite3.Row
    return [dict(r) for r in conn.execute(sql,args)]

def mean(values):
    vals=[v for v in values if v is not None]
    return round(sum(vals)/len(vals),1) if vals else None

def extract_agents(raw):
    if raw is None:
        return []
    value=raw
    if isinstance(value,str):
        try:
            value=json.loads(value)
        except (json.JSONDecodeError,TypeError):
            value=re.findall(r"[A-Za-z][A-Za-z0-9_/-]*",value)
    if isinstance(value,dict):
        value=[value]
    if not isinstance(value,(list,tuple)):
        value=[value]
    names=[]
    for item in value:
        if isinstance(item,dict):
            name=next((item.get(k) for k in ("name","agent","agent_name","character") if item.get(k)),None)
        else:
            name=item
        if name is not None:
            cleaned=str(name).strip().strip("[](){}\\\"'")
            if cleaned and cleaned.lower() not in ("unknown","none","null"):
                names.append(cleaned.title())
    return list(dict.fromkeys(names))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--valorant-dir",required=True)
    ap.add_argument("--lol-dir",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    vd=Path(a.valorant_dir); ld=Path(a.lol_dir); out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    vdb=sqlite3.connect(vd/"valorant_vct_2025_2026.sqlite")
    ldb=sqlite3.connect(ld/"lol_player_master_2025_2026.sqlite")
    matches=rows(vdb,"SELECT * FROM matches WHERE listing_status='Completed' AND is_showmatch=0")
    teams={r["team_id"]:r for r in rows(vdb,"SELECT * FROM teams")}
    players={r["player_id"]:r for r in rows(vdb,"SELECT * FROM players")}
    team_stats=collections.defaultdict(lambda:{"series":0,"seriesWins":0,"mapWins":0,"maps":0,"regions":collections.Counter()})
    map_stats=collections.defaultdict(lambda:{"games":0,"wins":collections.Counter(),"teamGames":collections.Counter()})
    match_by_id={m["match_id"]:m for m in matches}
    for m in matches:
        t0,t1=m["team0_id"],m["team1_id"]
        if t0 not in teams or t1 not in teams: continue
        for tid in (t0,t1):
            team_stats[tid]["series"]+=1
            team_stats[tid]["regions"][m.get("region") or "Unknown"]+=1
        if m["score0"]>m["score1"]: team_stats[t0]["seriesWins"]+=1
        elif m["score1"]>m["score0"]: team_stats[t1]["seriesWins"]+=1
    map_rows=rows(vdb,"SELECT * FROM maps")
    for mr in map_rows:
        m=match_by_id.get(mr["match_id"])
        if not m: continue
        t0,t1=m["team0_id"],m["team1_id"]
        if t0 not in teams or t1 not in teams: continue
        name=mr.get("map_name") or "Unknown"
        s=map_stats[name]; s["games"]+=1
        s["teamGames"][t0]+=1; s["teamGames"][t1]+=1
        team_stats[t0]["maps"]+=1; team_stats[t1]["maps"]+=1
        if mr["score0"]>mr["score1"]:
            s["wins"][t0]+=1; team_stats[t0]["mapWins"]+=1
        elif mr["score1"]>mr["score0"]:
            s["wins"][t1]+=1; team_stats[t1]["mapWins"]+=1
    player_rows=rows(vdb,"""SELECT pm.*,m.team0_id,m.team1_id,mp.map_name FROM player_map pm
       JOIN matches m USING(match_id)
       JOIN maps mp ON mp.game_id=pm.game_id
       WHERE m.listing_status='Completed' AND m.is_showmatch=0""")
    grouped=collections.defaultdict(lambda:collections.defaultdict(list))
    for r in player_rows:
        tid=r["team0_id"] if r["team_idx"]==0 else r["team1_id"] if r["team_idx"]==1 else None
        if tid is not None: grouped[tid][r["player_id"]].append(r)
    team_out=[]
    for tid,t in teams.items():
        st=team_stats[tid]; pout=[]
        for pid,rs in grouped[tid].items():
            p=players.get(pid,{})
            agents=collections.Counter()
            agent_kills=collections.defaultdict(list)
            agent_map_kills=collections.defaultdict(list)
            for rr in rs:
                row_agents=extract_agents(rr.get("agents"))
                map_name=rr.get("map_name") or "Unknown"
                for ag in row_agents:
                    agents[ag]+=1
                    if rr.get("kills_all") is not None:
                        agent_kills[ag].append(rr.get("kills_all"))
                        agent_map_kills[(ag,map_name)].append(rr.get("kills_all"))
            agent_stats=[{"name":ag,"maps":len(values),"avgKills":mean(values)}
                         for ag,values in agent_kills.items()]
            agent_stats.sort(key=lambda x:(x["maps"],x["avgKills"] or 0),reverse=True)
            agent_map_stats=[{"agent":ag,"map":mn,"maps":len(values),"avgKills":mean(values)}
                             for (ag,mn),values in agent_map_kills.items()]
            agent_map_stats.sort(key=lambda x:(x["agent"],x["map"]))
            pout.append({"id":pid,"name":p.get("player_name") or "Unknown","country":p.get("country") or "",
              "maps":len(rs),"avgKills":mean([x.get("kills_all") for x in rs]),
              "avgDeaths":mean([x.get("deaths_all") for x in rs]),"avgAssists":mean([x.get("assists_all") for x in rs]),
              "avgAcs":mean([x.get("acs_all") for x in rs]),"avgAdr":mean([x.get("adr_all") for x in rs]),
              "avgRating":mean([x.get("rating_all") for x in rs]),"avgKast":mean([x.get("kast_all") for x in rs]),
              "agents":[{"name":k,"maps":v} for k,v in agents.most_common(5)],
              "agentStats":agent_stats,"agentMapStats":agent_map_stats})
        pout.sort(key=lambda x:(x["maps"],x["avgKills"] or 0),reverse=True)
        mstats=[]
        for mn,ms in map_stats.items():
            n=ms["teamGames"][tid]
            if n:
                w=ms["wins"][tid]
                mstats.append({"map":mn,"games":n,"wins":w,"losses":n-w,"winRate":round(100*w/n,1)})
        mstats.sort(key=lambda x:x["games"],reverse=True)
        team_out.append({"id":tid,"name":t["team_name"],"country":t.get("country") or "",
          "series":st["series"],"seriesWins":st["seriesWins"],
          "seriesWinRate":round(100*st["seriesWins"]/st["series"],1) if st["series"] else None,
          "maps":st["maps"],"mapWins":st["mapWins"],
          "mapWinRate":round(100*st["mapWins"]/st["maps"],1) if st["maps"] else None,
          "regions":[{"name":k,"matches":v} for k,v in st["regions"].most_common()],
          "mapStats":mstats,"players":pout})
    team_out.sort(key=lambda x:(x["seriesWins"],x["mapWinRate"] or 0),reverse=True)
    maps_out=[]
    for name,ms in sorted(map_stats.items(),key=lambda x:x[1]["games"],reverse=True):
        ranked=sorted([{"teamId":tid,"team":teams[tid]["team_name"],"wins":n,"games":ms["teamGames"][tid]}
          for tid,n in ms["wins"].items()],key=lambda x:x["wins"],reverse=True)
        maps_out.append({"name":name,"games":ms["games"],"teams":ranked[:20]})
    lol_players=rows(ldb,"SELECT player_id,handle,games_observed,first_seen_utc,last_seen_utc,team_names,roles_observed,leagues_observed,identity_status FROM players ORDER BY games_observed DESC")
    for p in lol_players:
        p["teams"]=(p.pop("team_names") or "").split(" | ") if p.get("team_names") else []
        p["roles"]=(p.pop("roles_observed") or "").split(" | ") if p.get("roles_observed") else []
        p["leagues"]=(p.pop("leagues_observed") or "").split(" | ") if p.get("leagues_observed") else []
        p["gamesObserved"]=p.pop("games_observed"); p["firstSeen"]=p.pop("first_seen_utc"); p["lastSeen"]=p.pop("last_seen_utc")
        p["identityStatus"]=p.pop("identity_status")
    lol_teams=rows(ldb,"""SELECT team_name_observed AS name,SUM(games_with_team) AS games,
       COUNT(DISTINCT player_source_identity_key) AS players
       FROM player_team_observations GROUP BY team_name_observed ORDER BY games DESC""")
    meta={"window":{"from":"2025-01-01","to":"2026-12-31"},
      "valorant":{"source":"VCT Reference","matches":len(matches),"maps":len(map_rows),"players":len(players),"teams":len(teams),
       "rounds":vdb.execute("SELECT COUNT(*) FROM rounds").fetchone()[0],
       "coverage":"Tier-1 VCT and qualifying regional events represented by the source; this is not a complete feed of every amateur/open competition."},
      "lol":{"source":"ChainCC Open Dataset","players":len(lol_players),"teamObservations":ldb.execute("SELECT COUNT(*) FROM player_team_observations").fetchone()[0],
       "coverage":"Current imported source provides provisional player identities and observed team associations, not player-by-player game kills, KDA or champion stats."},
      "cs2":{"source":None,"matches":0,"coverage":"No CS2 historical dataset has been imported yet."}}
    payload={"meta":meta,"valorant":{"maps":maps_out,"teams":team_out},
      "lol":{"players":lol_players,"teams":lol_teams},"cs2":{"maps":[],"teams":[],"players":[]}}
    with open(out/"esports.json","w",encoding="utf-8") as f: json.dump(payload,f,separators=(",",":"),ensure_ascii=False)
    print(json.dumps({"valorant_teams":len(team_out),"valorant_maps":len(maps_out),"lol_players":len(lol_players),"lol_teams":len(lol_teams),"output_bytes":(out/"esports.json").stat().st_size},indent=2))
    vdb.close(); ldb.close()
if __name__=="__main__": main()
