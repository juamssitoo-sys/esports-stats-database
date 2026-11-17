-- Counter-Strike 2 / HLTV-oriented extension.
-- Apply after database/schema.sql. Source values remain nullable when not published.
INSERT INTO sources (slug,name,base_url,notes)
VALUES ('hltv','HLTV.org','https://www.hltv.org/','Community Counter-Strike coverage, match pages, events and player statistics')
ON CONFLICT (slug) DO NOTHING;

CREATE TABLE IF NOT EXISTS cs2_map_stats (
  id BIGSERIAL PRIMARY KEY,
  match_map_id BIGINT NOT NULL UNIQUE REFERENCES match_maps(id) ON DELETE CASCADE,
  team1_ct_rounds SMALLINT,
  team1_t_rounds SMALLINT,
  team2_ct_rounds SMALLINT,
  team2_t_rounds SMALLINT,
  overtime_rounds SMALLINT,
  source_url TEXT,
  raw JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS cs2_player_map_stats (
  id BIGSERIAL PRIMARY KEY,
  match_map_id BIGINT NOT NULL REFERENCES match_maps(id) ON DELETE CASCADE,
  player_id BIGINT REFERENCES players(id),
  team_id BIGINT REFERENCES teams(id),
  kills SMALLINT,
  deaths SMALLINT,
  assists SMALLINT,
  flash_assists SMALLINT,
  headshots SMALLINT,
  headshot_pct NUMERIC(6,2),
  adr NUMERIC(7,2),
  kast_pct NUMERIC(6,2),
  rating NUMERIC(7,3),
  opening_kills SMALLINT,
  opening_deaths SMALLINT,
  multi_kills_2k SMALLINT,
  multi_kills_3k SMALLINT,
  multi_kills_4k SMALLINT,
  aces SMALLINT,
  clutches_won SMALLINT,
  source_player_id TEXT,
  raw JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (match_map_id, player_id)
);

CREATE INDEX IF NOT EXISTS idx_cs2_player_stats_player ON cs2_player_map_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_cs2_player_stats_team ON cs2_player_map_stats(team_id);
