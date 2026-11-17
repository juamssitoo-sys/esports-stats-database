'use client';
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Activity, ArrowLeft, Search, Swords, Trophy, Users, Map as MapIcon, RefreshCw } from "lucide-react";
import styles from "./cs2.module.css";

type Row = Record<string, any>;
type Data = { source:string; window:{from:string;to:string}; matches:number; pagesFetched:number; totalPagesAvailable:number; teams:Row[]; maps:Row[]; players:Row[]; recentMatches:Row[]; note:string };

const n = (v:any, d=1) => v == null ? "—" : Number(v).toFixed(d);
const pct = (v:any) => v == null ? "—" : `${Number(v).toFixed(1)}%`;

export default function CS2Page(){
 const [data,setData]=useState<Data|null>(null);
 const [loading,setLoading]=useState(true);
 const [error,setError]=useState("");
 const [search,setSearch]=useState("");
 const [mapFilter,setMapFilter]=useState("Todos");
 const [selectedTeam,setSelectedTeam]=useState<Row|null>(null);
 const load=()=>{setLoading(true);setError("");fetch("/api/cs2").then(async r=>{const j=await r.json();if(!r.ok)throw new Error(j.error||"Error consultando Cito API");return j;}).then(setData).catch(e=>setError(e.message)).finally(()=>setLoading(false));};
 useEffect(()=>{load();},[]);
 const teams=useMemo(()=> (data?.teams||[]).filter(t=>(!search||t.name.toLowerCase().includes(search.toLowerCase())) && (mapFilter==="Todos" || (data?.maps.find(m=>m.name===mapFilter)?.teams||[]).some((x:Row)=>x.teamId===t.id))).slice(0,150),[data,search,mapFilter]);
 const players=useMemo(()=> (data?.players||[]).filter(p=>(!selectedTeam || p.teams?.includes(selectedTeam.id)) && (!search || p.name.toLowerCase().includes(search.toLowerCase()))),[data,selectedTeam,search]);
 return <main className={styles.shell}>
  <header className={styles.header}>
   <Link href="/" className={styles.back}><ArrowLeft size={16}/> Volver a Esports Atlas</Link>
   <span className={styles.source}><i/> CONEXIÓN CITO API</span>
  </header>
  <section className={styles.hero}>
   <div className={styles.kicker}><Swords size={15}/> COUNTER-STRIKE 2 / COMPETITIVE INTELLIGENCE</div>
   <h1>CS2 <span>Stats</span></h1>
   <p>Resultados, mapas, equipos y rendimiento individual basados en registros disponibles de Cito API.</p>
   {data&&<div className={styles.period}>PERIODO {data.window.from} — {data.window.to}</div>}
  </section>
  {loading&&<div className={styles.state}><div className={styles.spinner}/> Consultando estadísticas de CS2…</div>}
  {error&&<div className={styles.error}><b>No se pudo cargar CS2</b><span>{error}</span><button onClick={load}><RefreshCw size={14}/> Reintentar</button></div>}
  {data&&<>
   <div className={styles.metrics}>
    <article><Trophy/><small>PARTIDAS ANALIZADAS</small><b>{data.matches.toLocaleString("es-PE")}</b></article>
    <article><MapIcon/><small>MAPAS REGISTRADOS</small><b>{data.maps.length.toLocaleString("es-PE")}</b></article>
    <article><Users/><small>EQUIPOS</small><b>{data.teams.length.toLocaleString("es-PE")}</b></article>
    <article><Activity/><small>JUGADORES</small><b>{data.players.length.toLocaleString("es-PE")}</b></article>
   </div>
   <div className={styles.notice}>{data.note} Se consultaron {data.pagesFetched} páginas de hasta 200 partidas; hay {data.totalPagesAvailable} páginas disponibles en el rango. Los datos ausentes no se interpretan como cero.</div>
   <section className={styles.section}>
    <div className={styles.sectionHead}><div><small>MAP POOL</small><h2>Rendimiento por mapa</h2><p>Selecciona un mapa para filtrar los equipos.</p></div><span>{data.maps.length} MAPAS</span></div>
    <div className={styles.mapGrid}>
     <button className={mapFilter==="Todos"?styles.mapActive:styles.mapCard} onClick={()=>setMapFilter("Todos")}><small>TODOS LOS MAPAS</small><b>{data.matches}</b><span>series consultadas</span></button>
     {data.maps.map((m,i)=><button key={m.name} className={mapFilter===m.name?styles.mapActive:styles.mapCard} onClick={()=>setMapFilter(mapFilter===m.name?"Todos":m.name)}><small>MAP {String(i+1).padStart(2,"0")}</small><b>{m.name}</b><span>{m.games} partidas</span><em>{m.teams?.[0]?.team||"Sin ganador destacado"} · {m.teams?.[0]?.wins||0} victorias</em></button>)}
    </div>
   </section>
   <section className={styles.section}>
    <div className={styles.sectionHead}><div><small>TEAM RANKING</small><h2>Equipos</h2><p>Clasificación por victorias en las series consultadas.</p></div><span>{teams.length} EQUIPOS</span></div>
    <div className={styles.toolbar}><div className={styles.search}><Search size={16}/><input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Buscar equipo o jugador…"/></div>{mapFilter!=="Todos"&&<button onClick={()=>setMapFilter("Todos")}>Quitar filtro: {mapFilter} ×</button>}</div>
    <div className={styles.tableWrap}><table><thead><tr><th>#</th><th>EQUIPO</th><th>PAÍS</th><th>SERIES</th><th>VICTORIAS</th><th>WIN RATE</th><th>MAPAS GANADOS</th></tr></thead><tbody>{teams.map((t,i)=><tr key={t.id} onClick={()=>setSelectedTeam(t)} className={selectedTeam?.id===t.id?styles.chosen:""}><td>{String(i+1).padStart(2,"0")}</td><td><b>{t.name}</b></td><td>{t.country||"—"}</td><td>{t.matches}</td><td>{t.wins}</td><td>{pct(t.winRate)}</td><td>{t.mapWins}</td></tr>)}</tbody></table>{teams.length===0&&<div className={styles.empty}>No hay equipos para este filtro.</div>}</div>
   </section>
   <section className={styles.section}>
    <div className={styles.sectionHead}><div><small>PLAYER PERFORMANCE</small><h2>{selectedTeam? `Jugadores · ${selectedTeam.name}` : "Estadísticas de jugadores"}</h2><p>Promedios por mapa de los registros disponibles.</p></div><span>{players.length} JUGADORES</span></div>
    {selectedTeam&&<button className={styles.clear} onClick={()=>setSelectedTeam(null)}>Ver todos los jugadores ×</button>}
    <div className={styles.tableWrap}><table><thead><tr><th>JUGADOR</th><th>MAPAS</th><th>KILLS PROM.</th><th>DEATHS PROM.</th><th>ADR</th><th>KAST</th><th>RATING</th><th>HEADSHOT %</th></tr></thead><tbody>{players.slice(0,150).map(p=><tr key={p.id}><td><b>{p.name}</b></td><td>{p.maps}</td><td>{n(p.avgKills)}</td><td>{n(p.avgDeaths)}</td><td>{n(p.adr)}</td><td>{pct(p.kast)}</td><td>{n(p.rating,2)}</td><td>{pct(p.headshotPercent)}</td></tr>)}</tbody></table>{players.length===0&&<div className={styles.empty}>No hay estadísticas individuales para esta selección.</div>}</div>
   </section>
   <section className={styles.section}>
    <div className={styles.sectionHead}><div><small>MATCH HISTORY</small><h2>Partidas recientes del periodo</h2></div><span>{data.recentMatches.length} REGISTROS</span></div>
    <div className={styles.matches}>{data.recentMatches.map(m=><article key={m.id}><div><b>{m.team1}</b><span>{m.score1??"—"} : {m.score2??"—"}</span><b>{m.team2}</b></div><small>{m.event} · {m.date?new Date(m.date).toLocaleDateString("es-PE"):"Fecha no disponible"}</small></article>)}</div>
   </section>
  </>}
  <footer className={styles.footer}>ESPORTS ATLAS © 2026 · FUENTE: CITO API · CS2 EN BETA</footer>
 </main>;
}
