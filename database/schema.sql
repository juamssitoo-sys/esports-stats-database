-- Esports Stats Database — PostgreSQL 15+
-- All source-derived fields are nullable where providers may omit data.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS games (
  id SMALLSERIAL PRIMARY KEY,
  slug TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL
);
INSERT INTO games (slug, name) VALUES
 ('valorant','VALORANT'), ('league-of-legends','League of Legends'), ('counter-strike-2','Counter-Strike 2')
ON CONFLICT (slug) DO NOTHING;

CREATE TABLE IF NOT EXISTS sources (
  id BIGSERIAL PRIMARY KEY,
  slug TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  base_url TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
INSERT INTO sources (slug,name,base_url,notes) VALUES
 ('vlr-gg','VLR.gg','https://www.vlr.gg/','Community VALORANT results and statistics source')
ON CONFLICT (slug) DO NOTHING;

CREATE TABLE IF NOT EXISTS tournaments (
  id BIGSERIAL PRIMARY KEY,
  game_id SMALLINT NOT NULL REFERENCES games(id),
  source_id BIGINT REFERENCES sources(id),
  source_tournament_id TEXT,
  name TEXT NOT NULL,
  region TEXT,
  start_date DATE,
  end_date DATE,
  source_url TEXT,
  raw JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (source_id, source_tournament_id)
);

CREATE TABLE IF NOT EXISTS teams (
  id BIGSERIAL PRIMARY KEY,
  game_id SMALLINT NOT NULL REFERENCES games(id),
  source_id BIGINT REFERENCES sources(id),
  source_team_id TEXT,
  name TEXT NOT NULL,
  tag TEXT,
  region TEXT,
  country_code CHAR(2),
  source_url TEXT,
  raw JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (source_id, source_team_id)
);

CREATE TABLE IF NOT EXISTS players (
  id BIGSERIAL PRIMARY KEY,
  game_id SMALLINT NOT NULL REFERENCES games(id),
  source_id BIGINT REFERENCES sources(id),
  source_player_id TEXT,
  handle TEXT NOT NULL,
  real_name TEXT,
  country_code CHAR(2),
  source_url TEXT,
  raw JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (source_id, source_player_id)
);

CREATE TABLE IF NOT EXISTS team_rosters (
  id BIGSERIAL PRIMARY KEY,
  team_id BIGINT NOT NULL REFERENCES teams(id),
  player_id BIGINT NOT NULL REFERENCES players(id),
  joined_at DATE,
  left_at DATE,
  role TEXT,
  source_url TEXT,
  UNIQUE (team_id, player_id, joined_at)
);

CREATE TABLE IF NOT EXISTS matches (
  id BIGSERIAL PRIMARY KEY,
  game_id SMALLINT NOT NULL REFERENCES games(id),
  source_id BIGINT REFERENCES sources(id),
  tournament_id BIGINT REFERENCES tournaments(id),
  source_match_id TEXT,
  scheduled_at TIMESTAMPTZ,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  status TEXT,
  best_of SMALLINT,
  team1_id BIGINT REFERENCES teams(id),
  team2_id BIGINT REFERENCES teams(id),
  team1_score SMALLINT,
  team2_score SMALLINT,
  winner_team_id BIGINT REFERENCES teams(id),
  source_url TEXT,
  raw JSONB NOT NULL DEFAULT '{}'::jsonb,
  collected_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (source_id, source_match_id)
);

CREATE TABLE IF NOT EXISTS maps (
  id BIGSERIAL PRIMARY KEY,
  game_id SMALLINT NOT NULL REFERENCES games(id),
  name TEXT NOT NULL,
  source_map_id TEXT,
  UNIQUE (game_id, name)
);

CREATE TABLE IF NOT EXISTS match_maps (
  id BIGSERIAL PRIMARY KEY,
  match_id BIGINT NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
  map_id BIGINT REFERENCES maps(id),
  map_number SMALLINT NOT NULL,
  team1_rounds SMALLINT,
  team2_rounds SMALLINT,
  team1_attack_rounds SMALLINT,
  team1_defense_rounds SMALLINT,
  team2_attack_rounds SMALLINT,
  team2_defense_rounds SMALLINT,
  winner_team_id BIGINT REFERENCES teams(id),
  duration_seconds INTEGER,
  source_game_id TEXT,
  raw JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (match_id, map_number)
);

CREATE TABLE IF NOT EXISTS player_match_stats (
  id BIGSERIAL PRIMARY KEY,
  match_map_id BIGINT NOT NULL REFERENCES match_maps(id) ON DELETE CASCADE,
  player_id BIGINT REFERENCES players(id),
  team_id BIGINT REFERENCES teams(id),
  agent_or_character TEXT,
  kills SMALLINT,
  deaths SMALLINT,
  assists SMALLINT,
  rating NUMERIC(7,3),
  acs NUMERIC(8,2),
  adr NUMERIC(8,2),
  kast_pct NUMERIC(6,2),
  headshot_pct NUMERIC(6,2),
  first_kills SMALLINT,
  first_deaths SMALLINT,
  plants SMALLINT,
  defuses SMALLINT,
  econ_rating NUMERIC(8,2),
  source_player_id TEXT,
  raw JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (match_map_id, player_id)
);

CREATE TABLE IF NOT EXISTS round_stats (
  id BIGSERIAL PRIMARY KEY,
  match_map_id BIGINT NOT NULL REFERENCES match_maps(id) ON DELETE CASCADE,
  round_number SMALLINT NOT NULL,
  winning_team_id BIGINT REFERENCES teams(id),
  attacking_team_id BIGINT REFERENCES teams(id),
  round_type TEXT,
  plant_player_id BIGINT REFERENCES players(id),
  defuse_player_id BIGINT REFERENCES players(id),
  raw JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (match_map_id, round_number)
);

CREATE TABLE IF NOT EXISTS kill_events (
  id BIGSERIAL PRIMARY KEY,
  round_stat_id BIGINT NOT NULL REFERENCES round_stats(id) ON DELETE CASCADE,
  event_order SMALLINT,
  killer_player_id BIGINT REFERENCES players(id),
  victim_player_id BIGINT REFERENCES players(id),
  assister_player_id BIGINT REFERENCES players(id),
  weapon TEXT,
  is_first_blood BOOLEAN,
  event_time_ms INTEGER,
  raw JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- Immutable raw capture for replayability, re-parsing and audit.
CREATE TABLE IF NOT EXISTS source_payloads (
  id BIGSERIAL PRIMARY KEY,
  source_id BIGINT NOT NULL REFERENCES sources(id),
  game_id SMALLINT NOT NULL REFERENCES games(id),
  entity_type TEXT NOT NULL,
  source_entity_id TEXT,
  source_url TEXT,
  fetched_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  payload_hash TEXT NOT NULL,
  payload JSONB NOT NULL,
  parser_version TEXT NOT NULL DEFAULT '0.1.0',
  UNIQUE (source_id, entity_type, source_entity_id, payload_hash)
);

CREATE INDEX IF NOT EXISTS idx_matches_game_completed ON matches(game_id, completed_at);
CREATE INDEX IF NOT EXISTS idx_matches_tournament ON matches(tournament_id);
CREATE INDEX IF NOT EXISTS idx_match_maps_map ON match_maps(map_id);
CREATE INDEX IF NOT EXISTS idx_player_stats_player ON player_match_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_player_stats_map ON player_match_stats(match_map_id);
CREATE INDEX IF NOT EXISTS idx_round_stats_map ON round_stats(match_map_id);
CREATE INDEX IF NOT EXISTS idx_payloads_entity ON source_payloads(source_id, entity_type, source_entity_id);
CREATE INDEX IF NOT EXISTS idx_payloads_fetched ON source_payloads(fetched_at);
