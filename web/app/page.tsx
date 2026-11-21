'use client';
import { useEffect, useMemo, useState } from 'react';
import { Activity, ChevronDown, ChevronRight, Crosshair, Gamepad2, Globe2, Search, Shield, Swords, Trophy, Users, X } from 'lucide-react';

type AnyRow = Record<string, any>;
type Dataset = { meta: AnyRow; valorant: { maps: AnyRow[]; teams: AnyRow[] }; lol: { players: AnyRow[]; teams: AnyRow[] }; cs2: { maps: AnyRow[]; teams: AnyRow[]; players: AnyRow[] } };
const mapArtwork:Record<string,string> = {
 Lotus:'https://media.valorant-api.com/maps/2fe4ed3a-450a-948b-6d6b-e89a78e680a9/splash.png',
 Ascent:'https://media.valorant-api.com/maps/7eaecc1b-4337-bbf6-6ab9-04b8f06b3319/splash.png',
 Icebox:'https://media.valorant-api.com/maps/e2ad5c54-4114-a870-9641-8ea21279579a/splash.png',
 Pearl:'https://cmsassets.rgpub.io/sanity/images/dsfx7636/news_live/824602886bfdcfc19d0858e16bcf953dbd15946c-1920x1080.jpg',
 Split:'https://wallpaperaccess.com/full/6192324.jpg',
 Haven:'https://media.valorant-api.com/maps/2bee0dc9-4ffe-519b-1cbd-7fbe763a6047/splash.png',
 Sunset:'https://imgoss.suozhang.cn/maps/92584fbe-486a-b1b2-9faa-39b0f486b498/splash.png',
 Breeze:'https://media.dexerto.com/media/valorant-map-breeze-splash.png?format=auto&quality=75&width=768',
 Corrode:'https://c-valorant-api.op.gg/Assets/Maps/1C18AB1F-420D-0D8B-71D0-77AD3C439115_splash.png?image=q_auto%3Agood%2Cf_webp&v=1771503167',
 Fracture:'https://cmsassets.rgpub.io/sanity/images/dsfx7636/news_live/881eda9ac7e56cb18efff9759ac6b2ba5b232a56-1920x1080.jpg?auto=format&fit=fill&q=80&w=1920',
 Summit:'https://cmsassets.rgpub.io/sanity/images/dsfx7636/news_live/ff7f89ff681da27cfec24bf61986c23fb2aba543-1920x1080.jpg',
 Abyss:'https://media.valorant-api.com/maps/224b0a95-48b9-f703-1bd8-67aca101a61f/splash.png',
 Bind:'https://assets-global.website-files.com/5c1bb997cb1dd611a0e6c8ce/5fb57df14ad8ff6a6a085432_WestStudio-Valorant-84.jpg',
 default:'https://media.valorant-api.com/maps/2fe4ed3a-450a-948b-6d6b-e89a78e680a9/splash.png'
};
const games = [
 {id:'valorant',label:'VALORANT',color:'red',icon:Crosshair},
 {id:'lol',label:'LEAGUE OF LEGENDS',color:'gold',icon:Shield},
 {id:'cs2',label:'COUNTER-STRIKE 2',color:'blue',icon:Swords}
] as const;
const number=(v:any,d=1)=>v===null||v===undefined?'—':Number(v).toFixed(d);
const percent=(v:any)=>v===null||v===undefined?'—':String(Number(v).toFixed(1))+'%';

export default function Home(){
 const [data,setData]=useState<Dataset|null>(null),[loading,setLoading]=useState(true);
 const [game,setGame]=useState<'valorant'|'lol'|'cs2'>('valorant'),[search,setSearch]=useState('');
 const [mapFilter,setMapFilter]=useState('Todos'),[region,setRegion]=useState('Todas');
 const [selectedTeam,setSelectedTeam]=useState<AnyRow|null>(null),[season,setSeason]=useState('2025–2026');
 useEffect(()=>{fetch('/data/esports.json').then(r=>{if(!r.ok)throw new Error('No se pudo cargar el dataset');return r.json();}).then(setData).catch(console.error).finally(()=>setLoading(false));},[]);
 const vTeams=data?.valorant.teams??[],vMaps=data?.valorant.maps??[];
 const vRegions=useMemo(()=>['Todas',...Array.from(new Set(vTeams.flatMap(t=>(t.regions??[]).map((r:AnyRow)=>r.name)))).sort()], [vTeams]);
 const filteredVTeams=useMemo(()=>vTeams.filter(t=>{
  const q=search.toLowerCase(),inSearch=!q||t.name.toLowerCase().includes(q)||t.players.some((p:AnyRow)=>p.name.toLowerCase().includes(q));
  const inMap=mapFilter==='Todos'||t.mapStats.some((m:AnyRow)=>m.map===mapFilter),inRegion=region==='Todas'||t.regions.some((r:AnyRow)=>r.name===region);
  return inSearch&&inMap&&inRegion;
 }).sort((a,b)=>mapFilter==='Todos'?b.seriesWins-a.seriesWins:(b.mapStats.find((m:AnyRow)=>m.map===mapFilter)?.wins??0)-(a.mapStats.find((m:AnyRow)=>m.map===mapFilter)?.wins??0)),[vTeams,search,mapFilter,region]);
 const lolTeams=data?.lol.teams??[],lolPlayers=data?.lol.players??[];
 const filteredLolTeams=lolTeams.filter(t=>!search||t.name.toLowerCase().includes(search.toLowerCase()));
 const filteredLolPlayers=lolPlayers.filter(p=>{const q=search.toLowerCase(),teamOk=!selectedTeam||p.teams?.includes(selectedTeam.name);return teamOk&&(!q||p.handle.toLowerCase().includes(q)||p.teams?.some((t:string)=>t.toLowerCase().includes(q)));});
 const changeGame=(id:'valorant'|'lol'|'cs2')=>{if(id==='cs2'){window.location.href='/cs2';return;}setGame(id);setSearch('');setMapFilter('Todos');setRegion('Todas');setSelectedTeam(null);};

 return <main className={'app-shell '+(game==='valorant'?'valorant-theme':'')}>
  <aside className="sidebar">
   <div className="brand"><div className="brand-mark"><Activity size={19}/></div><div><b>ESPORTS<span>ATLAS</span></b><small>DATA INTELLIGENCE</small></div></div>
   <div className="side-label">PLATAFORMA</div>
   <nav className="game-nav">{games.map(g=>{const Icon=g.icon;return <button key={g.id} onClick={()=>changeGame(g.id)} className={'nav-game '+(game===g.id?'active':'')}><span className={'nav-icon '+g.color}><Icon size={17}/></span><span>{g.label}</span>{game===g.id&&<ChevronRight size={15} className="nav-arrow"/>}</button>;})}</nav>
   <div className="side-spacer"/>
   <div className="sidebar-note"><div className="live-dot"/><span>BASE HISTÓRICA</span><b>2025 — 2026</b><small>Datos sujetos a cobertura de cada fuente.</small></div>
   <div className="sidebar-footer">ESPORTS ATLAS <span>v1.0.0</span></div>
  </aside>
  <section className="main-area">
   <header className="topbar"><div className="breadcrumb">CENTRO DE DATOS <ChevronRight size={13}/><b>{games.find(g=>g.id===game)?.label}</b></div><div className="topbar-right"><span className="data-status"><i/> DATOS CON FUENTE</span><div className="avatar">EA</div></div></header>
   <div className="content">
    {game==='valorant'?<div className="valorant-command-hero">
     <div className="vch-topline"><span><i/> VCT // INTELLIGENCE DIVISION</span><span>PROTOCOLO 07 <b>● EN LÍNEA</b></span></div>
     <div className="vch-main">
      <div className="vch-copy"><div className="eyebrow">COMPETITIVE OPERATIONS · 2025—2026</div><h1>EL CAMPO<br/><span>DE DATOS.</span></h1><p>Analiza el meta. Domina los mapas. Estudia a cada equipo.</p><div className="vch-actions"><span className="vch-period">TEMPORADA <b>2025 — 2026</b></span><span className="vch-source">VCT REFERENCE DATABASE</span></div></div>
      <div className="vch-visual" aria-hidden="true"><div className="vch-orbit vch-orbit-one"/><div className="vch-orbit vch-orbit-two"/><div className="vch-reticle"><i/><b>V</b><span>VALORANT</span></div><div className="vch-coordinate">35° 41' 22.4"N<br/>139° 41' 30.1"E</div><div className="vch-vertical">TACTICAL COMBAT // EPISODE 09</div><div className="vch-side-index">07</div></div>
     </div>
     <div className="vch-bottomline"><span>PRECISION IS THE DIFFERENCE</span><span>SELECT · ANALYZE · EXECUTE</span><span>EST. 2020 / VCT</span></div>
    </div>:<div className="page-heading"><div><div className="eyebrow">COMPETITIVE INTELLIGENCE / {game.toUpperCase()}</div><h1>{game==='lol'?'League of Legends':'Counter-Strike 2'} <span>Stats</span></h1><p>Explora mapas, equipos, jugadores y rendimiento competitivo.</p></div><div className="period-badge"><span>PERIODO</span><b>2025 — 2026</b></div></div>}
    <div className="game-switch">{games.map(g=><button key={g.id} className={game===g.id?'selected':''} onClick={()=>changeGame(g.id)}><span className={'switch-dot '+g.color}/>{g.label}</button>)}</div>
    {loading?<div className="loading"><div className="loader"/><span>Cargando base estadística...</span></div>:!data?<div className="empty-state"><Activity/><h2>No se pudo cargar la base de datos</h2><p>Verifica que el archivo de estadísticas esté publicado.</p></div>:<>
     {game==='valorant'&&<>
      <div className="stats-grid">
       <Metric icon={<Trophy/>} label="SERIES REGISTRADAS" value={data.meta.valorant.matches.toLocaleString('es-PE')} note="Partidas completadas"/>
       <Metric icon={<Gamepad2/>} label="MAPAS JUGADOS" value={data.meta.valorant.maps.toLocaleString('es-PE')} note="Mapas con resultado"/>
       <Metric icon={<Users/>} label="JUGADORES" value={data.meta.valorant.players.toLocaleString('es-PE')} note="Identidades de la fuente"/>
       <Metric icon={<Shield/>} label="EQUIPOS" value={data.meta.valorant.teams.toLocaleString('es-PE')} note="Equipos identificados"/>
      </div>
      <div className="coverage-banner"><div className="coverage-icon"><Activity size={17}/></div><div><b>Alcance de los datos</b><span>{data.meta.valorant.coverage}</span></div><span className="source-tag">VCT REFERENCE</span></div>
      <section className="section-block">
       <div className="section-title"><div><div className="eyebrow">MAP POOL</div><h2>Estadísticas por mapa</h2><p>Selecciona un mapa para filtrar el rendimiento de los equipos.</p></div><span className="section-count">{vMaps.length} MAPAS</span></div>
       <div className="map-grid">{vMaps.map((m:AnyRow,i:number)=><button key={m.name} onClick={()=>setMapFilter(mapFilter===m.name?'Todos':m.name)} className={'map-card '+(mapFilter===m.name?'map-active':'')}><div className={'map-art map-art-'+(i%6)}><img className="map-art-image" src={mapArtwork[m.name]??mapArtwork.default} alt={`Arte oficial del mapa ${m.name}`} loading="lazy" decoding="async"/><span>MAP {String(i+1).padStart(2,'0')}</span><b>{m.name.toUpperCase()}</b><small>{m.games.toLocaleString('es-PE')} PARTIDAS</small></div><div className="map-card-bottom"><span>Más victorias</span><b>{m.teams?.[0]?.team??'—'}</b><strong>{m.teams?.[0]?.wins??0} <small>W</small></strong></div></button>)}</div>
       {mapFilter!=='Todos'&&<button className="clear-filter" onClick={()=>setMapFilter('Todos')}><X size={13}/> Quitar filtro: {mapFilter}</button>}
      </section>
      <section className="section-block">
       <div className="section-title"><div><div className="eyebrow">TEAM PERFORMANCE</div><h2>Equipos</h2><p>Victorias en series, mapas y rendimiento por jugador.</p></div><span className="section-count">{filteredVTeams.length} EQUIPOS</span></div>
       <div className="toolbar"><div className="search-box"><Search size={16}/><input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Buscar equipo o jugador..."/></div><div className="select-wrap"><Globe2 size={14}/><select value={region} onChange={e=>setRegion(e.target.value)}>{vRegions.map(r=><option key={r}>{r}</option>)}</select><ChevronDown size={13}/></div></div>
       <div className="team-table-wrap"><table className="team-table"><thead><tr><th>#</th><th>EQUIPO</th><th>REGIÓN</th><th>{mapFilter==='Todos'?'SERIES GANADAS':'VICTORIAS EN MAPA'}</th><th>{mapFilter==='Todos'?'WIN RATE GENERAL':'WIN RATE EN MAPA'}</th><th>{mapFilter==='Todos'?'MAPAS GANADOS':'MAPAS JUGADOS'}</th><th/></tr></thead><tbody>{filteredVTeams.slice(0,50).map((t:AnyRow,i:number)=><tr key={t.id} onClick={()=>setSelectedTeam(t)} className="click-row"><td className="rank">{String(i+1).padStart(2,'0')}</td><td><div className="team-cell"><div className="team-logo">{t.name.slice(0,2).toUpperCase()}</div><b>{t.name}</b></div></td><td><span className="region-pill">{t.regions?.[0]?.name??t.country??'—'}</span></td><td><b>{mapFilter==='Todos'?t.seriesWins:(t.mapStats.find((m:AnyRow)=>m.map===mapFilter)?.wins??0)}</b><span className="muted"> / {mapFilter==='Todos'?t.series:(t.mapStats.find((m:AnyRow)=>m.map===mapFilter)?.games??0)}</span></td><td><div className="win-cell"><b>{percent(mapFilter==='Todos'?t.seriesWinRate:(t.mapStats.find((m:AnyRow)=>m.map===mapFilter)?.winRate??null))}</b><div className="mini-bar"><i style={{width:String(mapFilter==='Todos'?t.seriesWinRate??0:t.mapStats.find((m:AnyRow)=>m.map===mapFilter)?.winRate??0)+'%'}}/></div></div></td><td>{mapFilter==='Todos'?t.mapWins.toLocaleString('es-PE'):(t.mapStats.find((m:AnyRow)=>m.map===mapFilter)?.games??0)}</td><td><ChevronRight size={16}/></td></tr>)}</tbody></table>{filteredVTeams.length===0&&<div className="no-results">No se encontraron equipos con esos filtros.</div>}</div>
      </section>
      {selectedTeam&&<TeamPanel team={selectedTeam} onClose={()=>setSelectedTeam(null)} mapFilter={mapFilter}/>}
     </>}
     {game==='lol'&&<>
      <div className="stats-grid">
       <Metric icon={<Users/>} label="JUGADORES REGISTRADOS" value={data.meta.lol.players.toLocaleString('es-PE')} note="Identidades provisionales"/>
       <Metric icon={<Shield/>} label="OBSERVACIONES DE EQUIPO" value={data.meta.lol.teamObservations.toLocaleString('es-PE')} note="Relaciones jugador-equipo"/>
       <Metric icon={<Trophy/>} label="EQUIPOS" value={lolTeams.length.toLocaleString('es-PE')} note="Nombres detectados"/>
       <Metric icon={<Activity/>} label="ESTADO DE DATOS" value="PARCIAL" note="Falta detalle por partida"/>
      </div>
      <div className="coverage-banner warning"><div className="coverage-icon"><Activity size={17}/></div><div><b>Datos disponibles de League of Legends</b><span>{data.meta.lol.coverage}</span></div><span className="source-tag">CHAINCC</span></div>
      <section className="section-block"><div className="section-title"><div><div className="eyebrow">TEAM DIRECTORY</div><h2>Equipos registrados</h2><p>Selecciona un equipo para consultar jugadores observados y sus roles.</p></div><span className="section-count">{filteredLolTeams.length} EQUIPOS</span></div>
       <div className="toolbar"><div className="search-box"><Search size={16}/><input value={search} onChange={e=>{setSearch(e.target.value);setSelectedTeam(null)}} placeholder="Buscar equipo o jugador..."/></div></div>
       <div className="lol-team-grid">{filteredLolTeams.slice(0,60).map((t:AnyRow)=><button key={t.name} className={'lol-team-card '+(selectedTeam?.name===t.name?'chosen':'')} onClick={()=>setSelectedTeam(t)}><div className="team-logo">{t.name.slice(0,2).toUpperCase()}</div><div><b>{t.name}</b><span>{t.players} jugadores observados</span></div><strong>{t.games}<small> juegos</small></strong><ChevronRight size={15}/></button>)}</div>
      </section>
      <section className="section-block"><div className="section-title"><div><div className="eyebrow">PLAYER DIRECTORY</div><h2>{selectedTeam?'Jugadores · '+selectedTeam.name:'Registro de jugadores'}</h2><p>Historial de equipos, roles y ligas detectadas.</p></div><span className="section-count">{filteredLolPlayers.length.toLocaleString('es-PE')} JUGADORES</span></div>
       <div className="player-list">{filteredLolPlayers.slice(0,100).map((p:AnyRow)=><div className="lol-player-row" key={p.player_id}><div className="player-avatar">{p.handle.slice(0,2).toUpperCase()}</div><div className="player-main"><b>{p.handle}</b><span>{p.teams?.join(' · ')||'Equipo no identificado'}</span></div><div className="player-meta"><b>{p.gamesObserved}</b><span>JUEGOS OBS.</span></div><div className="player-meta"><b>{p.roles?.join(', ')||'—'}</b><span>ROLES</span></div><div className="player-meta"><b>{p.leagues?.slice(0,2).join(', ')||'—'}</b><span>LIGAS</span></div></div>)}</div>
       <div className="notice"><b>Importante:</b> esta versión todavía no tiene estadísticas por partida de LoL. No se mostrarán kills, KDA ni campeones promedio hasta importar una fuente con esos registros.</div>
      </section>
     </>}
     {game==='cs2'&&<div className="cs2-empty"><div className="cs2-emblem"><Swords size={34}/></div><div className="eyebrow">COUNTER-STRIKE 2 / DATA INGESTION</div><h2>La estructura de CS2 está preparada.</h2><p>La sección tendrá mapas, equipos, series, jugadores, kills, ADR, K/D, headshot %, armas y rendimiento por mapa. Todavía no se ha importado una fuente histórica validada para 2025–2026.</p><div className="cs2-checklist"><span><i/> Directorio de equipos y jugadores</span><span><i/> Resultados y estadísticas por mapa</span><span><i/> Perfiles individuales y comparativas</span></div><span className="coming-soon">DATOS PENDIENTES DE INGESTA</span></div>}
    </>}
    <footer className="page-footer"><span>ESPORTS ATLAS © 2026</span><span>FUENTES Y COBERTURA VARÍAN POR JUEGO · DATOS NO DISPONIBLES NO SE INTERPRETAN COMO CERO</span></footer>
   </div>
  </section>
 </main>;
}

function Metric({icon,label,value,note}:{icon:React.ReactNode;label:string;value:string;note:string}){return <div className="metric-card"><div className="metric-top"><span>{label}</span><i>{icon}</i></div><strong>{value}</strong><small>{note}</small></div>;}

function TeamPanel({team,onClose,mapFilter}:{team:AnyRow;onClose:()=>void;mapFilter:string}){
 const mapStats=(team.mapStats??[]).filter((m:AnyRow)=>mapFilter==='Todos'||m.map===mapFilter); const players=(team.players??[]).map((p:AnyRow)=>({...p,agentMapStats:(p.agentMapStats??[]).filter((a:AnyRow)=>mapFilter==='Todos'||a.map===mapFilter)})).filter((p:AnyRow)=>mapFilter==='Todos'||p.agentMapStats.length>0);
 return <div className="detail-overlay" onClick={onClose}><section className="detail-panel" onClick={e=>e.stopPropagation()}><div className="detail-head"><div><div className="eyebrow">TEAM PROFILE / VALORANT</div><h2>{team.name}</h2><span>{team.country?.toUpperCase()||'REGIÓN NO DISPONIBLE'} · {team.series} SERIES</span></div><button onClick={onClose} className="close-btn"><X/></button></div>
  <div className="detail-kpis"><div><small>SERIES GANADAS</small><b>{team.seriesWins}/{team.series}</b></div><div><small>WIN RATE</small><b>{percent(team.seriesWinRate)}</b></div><div><small>MAPAS GANADOS</small><b>{team.mapWins}/{team.maps}</b></div></div>
  <div className="detail-section"><div className="detail-title"><h3>Rendimiento por mapa</h3><span>{mapStats.length} MAPAS</span></div><div className="map-stat-list">{mapStats.map((m:AnyRow)=><div key={m.map}><b>{m.map}</b><span>{m.wins}W – {m.losses}L</span><div className="mini-bar"><i style={{width:String(m.winRate)+'%'}}/></div><strong>{percent(m.winRate)}</strong></div>)}</div></div>
  <div className="detail-section"><div className="detail-title"><h3>Jugadores y estadísticas</h3><span>{players.length} JUGADORES</span></div><div className="player-table-wrap"><table className="player-table"><thead><tr><th>JUGADOR</th><th>MAPAS</th><th>KILLS PROM.</th><th>ACS</th><th>ADR</th><th>RATING</th><th>KILLS PROM. POR AGENTE Y MAPA</th><th>AGENTES / MAPAS</th></tr></thead><tbody>{players.map((p:AnyRow)=><tr key={p.id}><td><b>{p.name}</b><small>{p.country?.toUpperCase()}</small></td><td>{p.maps}</td><td className="highlight-stat">{number(p.avgKills)}</td><td>{number(p.avgAcs,0)}</td><td>{number(p.avgAdr)}</td><td>{number(p.avgRating,2)}</td><td><div className="agent-chips">{p.agentMapStats?.length?p.agentMapStats.map((a:AnyRow)=><span key={a.agent+'-'+a.map} title={a.maps+' mapas de muestra'}>{a.agent} · {a.map}: {number(a.avgKills)} ({a.maps})</span>):'—'}</div></td><td><div className="agent-chips">{p.agents?.slice(0,3).map((a:AnyRow)=><span key={a.name}>{a.name} · {a.maps}</span>)}</div></td></tr>)}</tbody></table></div><p className="detail-footnote">Kills promedio calculadas por combinación de agente y mapa. El valor entre paréntesis indica la cantidad de mapas de la muestra para esa combinación.</p></div>
 </section></div>;
}
