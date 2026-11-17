import { NextResponse } from "next/server";

export const revalidate = 3600;
const BASE = "https://api.citoapi.com/api/v1";

type Row = Record<string, any>;

async function cito(path: string) {
  const key = process.env.CITO_API_KEY;
  if (!key) throw new Error("Falta configurar CITO_API_KEY en el entorno de Vercel.");
  const response = await fetch(`${BASE}${path}`, {
    headers: { "x-api-key": key, accept: "application/json" },
    next: { revalidate: 3600 },
  });
  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(`Cito API respondió ${response.status}: ${detail.slice(0, 240)}`);
  }
  const json = await response.json();
  if (json?.success === false) throw new Error(json?.error?.message || "Cito API no pudo completar la consulta.");
  return json;
}

const arr = (v: any): Row[] => Array.isArray(v) ? v : [];
const pickMaps = (match: Row): Row[] =>
  arr(match.maps).length ? arr(match.maps) :
  arr(match.included?.maps).length ? arr(match.included.maps) :
  arr(match.included?.games).length ? arr(match.included.games) : [];

export async function GET() {
  try {
    const today = new Date().toISOString().slice(0, 10);
    const first = await cito(`/cs2/matches/past?from=2025-01-01&to=${today}&limit=200&page=1&expand=full`);
    const firstRows = arr(first.data);
    const totalPages = Math.max(1, Number(first.meta?.totalPages || first.meta?.pagination?.totalPages || 1));
    const pagesToFetch = Math.min(totalPages, 5);
    const rest = await Promise.all(
      Array.from({ length: pagesToFetch - 1 }, (_, i) =>
        cito(`/cs2/matches/past?from=2025-01-01&to=${today}&limit=200&page=${i + 2}&expand=full`)
      )
    );
    const matches = [...firstRows, ...rest.flatMap(x => arr(x.data))];
    const teams = new Map<string, Row>();
    const teamStats = new Map<string, Row>();
    const mapStats = new Map<string, Row>();
    const players = new Map<string, Row>();
    const matchOut: Row[] = [];

    const getTeam = (id: string, name: string, country?: string) => {
      if (!teamStats.has(id)) {
        teams.set(id, { id, name, country: country || "" });
        teamStats.set(id, { id, name, country: country || "", matches: 0, wins: 0, maps: 0, mapWins: 0, players: new Set<string>() });
      }
      return teamStats.get(id)!;
    };

    for (const match of matches) {
      if (match.status !== "completed" || match.isForfeit || match.resultType === "forfeit") continue;
      const t1 = match.team1 || {};
      const t2 = match.team2 || {};
      const id1 = String(match.team1Id || t1.id || "");
      const id2 = String(match.team2Id || t2.id || "");
      const name1 = String(match.team1Name || t1.name || "Unknown");
      const name2 = String(match.team2Name || t2.name || "Unknown");
      if (!id1 || !id2) continue;
      const s1 = getTeam(id1, name1, t1.countryName);
      const s2 = getTeam(id2, name2, t2.countryName);
      s1.matches++; s2.matches++;
      if (match.winnerTeamId === id1) s1.wins++;
      if (match.winnerTeamId === id2) s2.wins++;

      for (const map of pickMaps(match)) {
        if (map.status === "map_not_played" || map.isForfeit || map.resultType === "forfeit") continue;
        const mapName = String(map.mapNameCanonical || map.mapName || map.map || "Unknown");
        const key = mapName.toLowerCase();
        if (!mapStats.has(key)) mapStats.set(key, { name: mapName, games: 0, teams: new Map<string, Row>() });
        const ms = mapStats.get(key)!;
        ms.games++;
        const winner = String(map.winnerTeamId || "");
        for (const [tid, tname] of [[id1, name1], [id2, name2]] as string[][]) {
          const ts = ms.teams.get(tid) || { teamId: tid, team: tname, games: 0, wins: 0 };
          ts.games++;
          if (winner && winner === tid) ts.wins++;
          ms.teams.set(tid, ts);
          const global = teamStats.get(tid)!;
          global.maps++;
          if (winner && winner === tid) global.mapWins++;
        }
        for (const stat of arr(map.playerStats || map.stats)) {
          const pid = String(stat.playerId || stat.id || stat.playerName || "");
          if (!pid) continue;
          const p = players.get(pid) || {
            id: pid, name: stat.playerName || "Unknown", teamIds: new Set<string>(),
            maps: 0, kills: 0, deaths: 0, assists: 0, adrSum: 0, adrN: 0,
            kastSum: 0, kastN: 0, ratingSum: 0, ratingN: 0,
            headshots: 0, hsN: 0, mapNames: new Map<string, number>(),
          };
          p.maps++; p.kills += Number(stat.kills || 0); p.deaths += Number(stat.deaths || 0);
          p.assists += Number(stat.assists || 0);
          if (stat.adr != null) { p.adrSum += Number(stat.adr); p.adrN++; }
          if (stat.kast != null) { p.kastSum += Number(stat.kast); p.kastN++; }
          if (stat.rating != null) { p.ratingSum += Number(stat.rating); p.ratingN++; }
          if (stat.headshotPercent != null) { p.headshots += Number(stat.headshotPercent); p.hsN++; }
          if (stat.teamId) p.teamIds.add(String(stat.teamId));
          p.mapNames.set(mapName, (p.mapNames.get(mapName) || 0) + 1);
          players.set(pid, p);
          const global = teamStats.get(String(stat.teamId || "")); if (global) global.players.add(pid);
        }
      }
      matchOut.push({
        id: match.id, date: match.startsAt, event: match.eventName || match.event?.name || "—",
        team1: name1, team2: name2, score1: match.team1Score, score2: match.team2Score,
        winner: match.winnerTeamId === id1 ? name1 : match.winnerTeamId === id2 ? name2 : "—",
        maps: pickMaps(match).map(m => m.mapNameCanonical || m.mapName || m.map).filter(Boolean),
      });
    }

    const teamsOut = [...teamStats.values()].map(t => ({
      id: t.id, name: t.name, country: t.country, matches: t.matches, wins: t.wins,
      winRate: t.matches ? Math.round(t.wins / t.matches * 1000) / 10 : null,
      maps: t.maps, mapWins: t.mapWins, players: t.players.size,
    })).sort((a,b) => b.wins - a.wins || (b.winRate ?? 0) - (a.winRate ?? 0));
    const mapsOut = [...mapStats.values()].map(m => ({
      name: m.name, games: m.games,
      teams: [...m.teams.values()].sort((a,b) => b.wins - a.wins).slice(0, 20),
    })).sort((a,b) => b.games - a.games);
    const playersOut = [...players.values()].map(p => ({
      id: p.id, name: p.name, maps: p.maps, kills: p.kills, deaths: p.deaths, assists: p.assists,
      avgKills: Math.round(p.kills / p.maps * 10) / 10,
      avgDeaths: Math.round(p.deaths / p.maps * 10) / 10,
      avgAssists: Math.round(p.assists / p.maps * 10) / 10,
      adr: p.adrN ? Math.round(p.adrSum / p.adrN * 10) / 10 : null,
      kast: p.kastN ? Math.round(p.kastSum / p.kastN * 1000) / 10 : null,
      rating: p.ratingN ? Math.round(p.ratingSum / p.ratingN * 100) / 100 : null,
      headshotPercent: p.hsN ? Math.round(p.headshots / p.hsN * 1000) / 10 : null,
      teams: [...p.teamIds],
      mapPreferences: [...p.mapNames.entries()].sort((a,b) => b[1]-a[1]).slice(0,5).map(([map,count]) => ({map,count})),
    })).sort((a,b) => b.maps - a.maps);
    return NextResponse.json({
      source: "Cito API", window: { from: "2025-01-01", to: today },
      matches: matchOut.length, pagesFetched: pagesToFetch, totalPagesAvailable: totalPages,
      teams: teamsOut, maps: mapsOut, players: playersOut, recentMatches: matchOut.slice(0,30),
      note: "Datos agregados de las páginas consultadas; la cobertura depende de los registros y estadísticas disponibles en Cito API.",
    });
  } catch (error: any) {
    return NextResponse.json({ error: error?.message || "No se pudo cargar CS2 desde Cito API." }, { status: 502 });
  }
}
