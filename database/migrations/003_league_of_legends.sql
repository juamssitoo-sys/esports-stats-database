-- League of Legends game-level extensions for Games of Legends (Gol.gg).
-- Apply after database/schema.sql. Nullable fields reflect source coverage.
INSERT INTO sources (slug, name, base_url, notes)
VALUES ('gol-gg', 'Games of Legends (Gol.gg)', 'https://gol.gg/esports/home/',
        'Competitive League of Legends statistics; public-page source specification only')
ON CONFLICT (slug) DO NOTHING;

CREATE TABLE IF NOT EXISTS lol_game_stats (
  id BIGSERIAL PRIMARY KEY,
  match_map_id BIGINT NOT NULL UNIQUE REFERENCES match_maps(id) ON DELETE CASCADE,
  patch TEXT,
  blue_team_id BIGINT REFERENCES teams(id),
  red_team_id BIGINT REFERENCES teams(id),
  blue_kills SMALLINT,
  red_kills SMALLINT,
  blue_gold BIGINT,
  red_gold BIGINT,
  blue_towers SMALLINT,
  red_towers SMALLINT,
  blue_inhibitors SMALLINT,
  red_inhibitors SMALLINT,
  blue_barons SMALLINT,
  red_barons SMALLINT,
  blue_dragons SMALLINT,
  red_dragons SMALLINT,
  blue_first_blood BOOLEAN,
  blue_first_tower BOOLEAN,
  source_game_id TEXT,
  raw JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS lol_player_game_stats (
  id BIGSERIAL PRIMARY KEY,
  match_map_id BIGINT NOT NULL REFERENCES match_maps(id) ON DELETE CASCADE,
  player_id BIGINT REFERENCES players(id),
  team_id BIGINT REFERENCES teams(id),
  champion TEXT,
  role TEXT,
  kills SMALLINT,
  deaths SMALLINT,
  assists SMALLINT,
  cs SMALLINT,
  gold BIGINT,
  damage_to_champions BIGINT,
  damage_taken BIGINT,
  vision_score NUMERIC(8,2),
  wards_placed SMALLINT,
  wards_killed SMALLINT,
  control_wards_bought SMALLINT,
  kill_participation_pct NUMERIC(6,2),
  source_player_id TEXT,
  raw JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (match_map_id, player_id)
);

CREATE TABLE IF NOT EXISTS lol_draft_picks (
  id BIGSERIAL PRIMARY KEY,
  match_map_id BIGINT NOT NULL REFERENCES match_maps(id) ON DELETE CASCADE,
  team_id BIGINT REFERENCES teams(id),
  player_id BIGINT REFERENCES players(id),
  champion TEXT NOT NULL,
  pick_order SMALLINT,
  is_ban BOOLEAN NOT NULL DEFAULT FALSE,
  raw JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (match_map_id, is_ban, pick_order)
);

CREATE INDEX IF NOT EXISTS idx_lol_player_stats_player ON lol_player_game_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_lol_player_stats_champion ON lol_player_game_stats(champion);
CREATE INDEX IF NOT EXISTS idx_lol_game_stats_patch ON lol_game_stats(patch);
