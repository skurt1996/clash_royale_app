"""
SQL statements used by db.py
Only multi-line statements are saved here.
"""

# Table creation queries
PLAYERS = """
CREATE TABLE IF NOT EXISTS `players`(
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY, -- is not retrieved from the api
    `tag` CHAR(10) NOT NULL, -- identifies a player,
    `name` VARCHAR(16) UNIQUE NOT NULL,
    `1v1_battle_count` INT UNSIGNED,
    `1v1_win_count` INT UNSIGNED,
    `1v1_three_crowns_win_count` INT UNSIGNED
)
"""

BATTLES = """
CREATE TABLE IF NOT EXISTS `battles`(
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY, -- is not retrieved from the api
    `time` DATETIME UNIQUE NOT NULL, -- identifies a match
    `type` VARCHAR(255) NOT NULL,
    `game_mode` VARCHAR(255) NOT NULL
)
"""

SCORES = """
CREATE TABLE IF NOT EXISTS `scores`(
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `crowns` INT NOT NULL,
    `king_tower_hp` INT NOT NULL,
    `princess_tower_1_hp` INT NOT NULL,
    `princess_tower_2_hp` INT NOT NULL,
    `elixir_leaked` DECIMAL(5, 2) NOT NULL,
    `deck_string` TEXT NOT NULL,
    `battle_id` INT UNSIGNED NOT NULL,
    `player_id` INT UNSIGNED NOT NULL,
    FOREIGN KEY (battle_id) REFERENCES battles(id),
    FOREIGN KEY (player_id) REFERENCES players(id)
)
"""

BATTLE_QUERY_FOR_DUPLICATION_CHECK = """
SELECT b.time, b.game_mode,
       s1.crowns, s1.player_id, s1.king_tower_hp,
       s1.princess_tower_1_hp, s1.princess_tower_2_hp,
       s1.elixir_leaked, s1.deck_string,
       s2.crowns, s2.player_id, s2.king_tower_hp,
       s2.princess_tower_1_hp, s2.princess_tower_2_hp,
       s2.elixir_leaked, s2.deck_string
FROM battles AS b
JOIN scores AS s1 ON b.id = s1.battle_id
JOIN scores AS s2 ON b.id = s2.battle_id AND s1.player_id != s2.player_id
WHERE s1.player_id < s2.player_id AND (b.time = '{}' OR b.time = '{}')
"""

ALL_BATTLES = """
SELECT b.time, b.game_mode,
       s1.crowns, s1.player_id, s1.king_tower_hp,
       s1.princess_tower_1_hp, s1.princess_tower_2_hp,
       s1.elixir_leaked, s1.deck_string,
       s2.crowns, s2.player_id, s2.king_tower_hp,
       s2.princess_tower_1_hp, s2.princess_tower_2_hp,
       s2.elixir_leaked, s2.deck_string
FROM battles AS b
JOIN scores AS s1 ON b.id = s1.battle_id
JOIN scores AS s2 ON b.id = s2.battle_id AND s1.player_id != s2.player_id
WHERE s1.player_id < s2.player_id 
ORDER BY b.time DESC
"""

ALL_BATTLES_WITH_LIMIT = """
SELECT b.time, b.game_mode,
       s1.crowns, s1.player_id, s1.king_tower_hp,
       s1.princess_tower_1_hp, s1.princess_tower_2_hp,
       s1.elixir_leaked, s1.deck_string,
       s2.crowns, s2.player_id, s2.king_tower_hp,
       s2.princess_tower_1_hp, s2.princess_tower_2_hp,
       s2.elixir_leaked, s2.deck_string
FROM battles AS b
JOIN scores AS s1 ON b.id = s1.battle_id
JOIN scores AS s2 ON b.id = s2.battle_id AND s1.player_id != s2.player_id
WHERE s1.player_id < s2.player_id 
AND b.time < %s
ORDER BY b.time DESC
LIMIT 10
"""

BATTLES_BY_GAME_MODE = """
SELECT b.time, b.game_mode,
       s1.crowns, s1.player_id, s1.king_tower_hp,
       s1.princess_tower_1_hp, s1.princess_tower_2_hp,
       s1.elixir_leaked, s1.deck_string,
       s2.crowns, s2.player_id, s2.king_tower_hp,
       s2.princess_tower_1_hp, s2.princess_tower_2_hp,
       s2.elixir_leaked, s2.deck_string
FROM battles AS b
JOIN scores AS s1 ON b.id = s1.battle_id
JOIN scores AS s2 ON b.id = s2.battle_id AND s1.player_id != s2.player_id
WHERE s1.player_id < s2.player_id 
AND b.game_mode = %s
ORDER BY b.time DESC
"""

BATTLES_BY_GAME_MODE_WITH_LIMIT = """
SELECT b.time, b.game_mode,
       s1.crowns, s1.player_id, s1.king_tower_hp,
       s1.princess_tower_1_hp, s1.princess_tower_2_hp,
       s1.elixir_leaked, s1.deck_string,
       s2.crowns, s2.player_id, s2.king_tower_hp,
       s2.princess_tower_1_hp, s2.princess_tower_2_hp,
       s2.elixir_leaked, s2.deck_string
FROM battles AS b
JOIN scores AS s1 ON b.id = s1.battle_id
JOIN scores AS s2 ON b.id = s2.battle_id AND s1.player_id != s2.player_id
WHERE s1.player_id < s2.player_id 
AND b.time < %s 
AND b.game_mode = %s
ORDER BY b.time DESC
LIMIT 10
"""

BATTLES_BY_PLAYER_TAG = """
SELECT b.time, b.game_mode,
       s1.crowns, s1.player_id, s1.king_tower_hp,
       s1.princess_tower_1_hp, s1.princess_tower_2_hp,
       s1.elixir_leaked, s1.deck_string,
       s2.crowns, s2.player_id, s2.king_tower_hp,
       s2.princess_tower_1_hp, s2.princess_tower_2_hp,
       s2.elixir_leaked, s2.deck_string
FROM battles AS b
JOIN scores AS s1 ON b.id = s1.battle_id
JOIN scores AS s2 ON b.id = s2.battle_id AND s1.player_id != s2.player_id
JOIN players AS p ON p.id = s1.player_id
WHERE b.time < %s 
AND p.tag = %s
ORDER BY b.time DESC
LIMIT 10
"""

BATTLES_BY_PLAYER_TAG_NO_LIMIT = """
SELECT b.time, b.game_mode,
       s1.crowns, s1.player_id, s1.king_tower_hp,
       s1.princess_tower_1_hp, s1.princess_tower_2_hp,
       s1.elixir_leaked, s1.deck_string,
       s2.crowns, s2.player_id, s2.king_tower_hp,
       s2.princess_tower_1_hp, s2.princess_tower_2_hp,
       s2.elixir_leaked, s2.deck_string
FROM battles AS b
JOIN scores AS s1 ON b.id = s1.battle_id
JOIN scores AS s2 ON b.id = s2.battle_id AND s1.player_id != s2.player_id
JOIN players AS p ON p.id = s1.player_id
WHERE b.time < %s 
AND p.tag = %s
ORDER BY b.time DESC
"""

BATTLES_BY_PLAYER_TAG_BY_GAME_MODE = """
SELECT b.time, b.game_mode,
       s1.crowns, s1.player_id, s1.king_tower_hp,
       s1.princess_tower_1_hp, s1.princess_tower_2_hp,
       s1.elixir_leaked, s1.deck_string,
       s2.crowns, s2.player_id, s2.king_tower_hp,
       s2.princess_tower_1_hp, s2.princess_tower_2_hp,
       s2.elixir_leaked, s2.deck_string
FROM battles AS b
JOIN scores AS s1 ON b.id = s1.battle_id
JOIN scores AS s2 ON b.id = s2.battle_id AND s1.player_id != s2.player_id
JOIN players AS p ON p.id = s1.player_id
WHERE b.time < %s 
AND p.tag = %s 
AND b.game_mode = %s
ORDER BY b.time DESC
LIMIT 10
"""

BATTLES_BY_PLAYER_TAG_BY_GAME_MODE_NO_LIMIT = """
SELECT b.time, b.game_mode,
       s1.crowns, s1.player_id, s1.king_tower_hp,
       s1.princess_tower_1_hp, s1.princess_tower_2_hp,
       s1.elixir_leaked, s1.deck_string,
       s2.crowns, s2.player_id, s2.king_tower_hp,
       s2.princess_tower_1_hp, s2.princess_tower_2_hp,
       s2.elixir_leaked, s2.deck_string
FROM battles AS b
JOIN scores AS s1 ON b.id = s1.battle_id
JOIN scores AS s2 ON b.id = s2.battle_id AND s1.player_id != s2.player_id
JOIN players AS p ON p.id = s1.player_id
WHERE b.time < %s 
AND p.tag = %s 
AND b.game_mode = %s
ORDER BY b.time DESC
"""

BATTLES_BY_PLAYER_TAG_BY_ENEMY_TAG = """
SELECT b.time, b.game_mode,
       s1.crowns, s1.player_id, s1.king_tower_hp,
       s1.princess_tower_1_hp, s1.princess_tower_2_hp,
       s1.elixir_leaked, s1.deck_string,
       s2.crowns, s2.player_id, s2.king_tower_hp,
       s2.princess_tower_1_hp, s2.princess_tower_2_hp,
       s2.elixir_leaked, s2.deck_string
FROM battles AS b
JOIN scores AS s1 ON b.id = s1.battle_id
JOIN scores AS s2 ON b.id = s2.battle_id AND s1.player_id != s2.player_id
JOIN players AS p1 ON p1.id = s1.player_id
JOIN players AS p2 ON p2.id = s2.player_id
WHERE b.time < %s 
AND p1.tag = %s 
AND p2.tag = %s
ORDER BY b.time DESC
LIMIT 10
"""

BATTLES_BY_PLAYER_TAG_BY_ENEMY_TAG_NO_LIMIT = """
SELECT b.time, b.game_mode,
       s1.crowns, s1.player_id, s1.king_tower_hp,
       s1.princess_tower_1_hp, s1.princess_tower_2_hp,
       s1.elixir_leaked, s1.deck_string,
       s2.crowns, s2.player_id, s2.king_tower_hp,
       s2.princess_tower_1_hp, s2.princess_tower_2_hp,
       s2.elixir_leaked, s2.deck_string
FROM battles AS b
JOIN scores AS s1 ON b.id = s1.battle_id
JOIN scores AS s2 ON b.id = s2.battle_id AND s1.player_id != s2.player_id
JOIN players AS p1 ON p1.id = s1.player_id
JOIN players AS p2 ON p2.id = s2.player_id
WHERE b.time < %s 
AND p1.tag = %s 
AND p2.tag = %s
ORDER BY b.time DESC
"""

BATTLES_BY_PLAYER_TAG_BY_GAME_MODE_BY_ENEMY_TAG = """
SELECT b.time, b.game_mode,
       s1.crowns, s1.player_id, s1.king_tower_hp,
       s1.princess_tower_1_hp, s1.princess_tower_2_hp,
       s1.elixir_leaked, s1.deck_string,
       s2.crowns, s2.player_id, s2.king_tower_hp,
       s2.princess_tower_1_hp, s2.princess_tower_2_hp,
       s2.elixir_leaked, s2.deck_string
FROM battles AS b
JOIN scores AS s1 ON b.id = s1.battle_id
JOIN scores AS s2 ON b.id = s2.battle_id AND s1.player_id != s2.player_id
JOIN players AS p1 ON p1.id = s1.player_id
JOIN players AS p2 ON p2.id = s2.player_id
WHERE b.time < %s
AND p1.tag = %s 
AND p2.tag = %s
AND b.game_mode = %s 
ORDER BY b.time DESC
LIMIT 10
"""

BATTLES_BY_PLAYER_TAG_BY_GAME_MODE_BY_ENEMY_TAG_NO_LIMIT = """
SELECT b.time, b.game_mode,
       s1.crowns, s1.player_id, s1.king_tower_hp,
       s1.princess_tower_1_hp, s1.princess_tower_2_hp,
       s1.elixir_leaked, s1.deck_string,
       s2.crowns, s2.player_id, s2.king_tower_hp,
       s2.princess_tower_1_hp, s2.princess_tower_2_hp,
       s2.elixir_leaked, s2.deck_string
FROM battles AS b
JOIN scores AS s1 ON b.id = s1.battle_id
JOIN scores AS s2 ON b.id = s2.battle_id AND s1.player_id != s2.player_id
JOIN players AS p1 ON p1.id = s1.player_id
JOIN players AS p2 ON p2.id = s2.player_id
WHERE b.time < %s
AND p1.tag = %s 
AND p2.tag = %s
AND b.game_mode = %s 
ORDER BY b.time DESC
"""