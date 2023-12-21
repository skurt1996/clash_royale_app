"""
This module is responsible for the interaction with the database.
Module is used by run.py to write to access the database.
"""
import os
import ast
from datetime import datetime, timedelta

import mysql.connector

from logger import configured_logger, TX_ROLLBACK_MSG
import sql_statements as sql
import data_retrieval as api
from utils import iso8601_to_datetime

ALLOWED_BATTLE_TYPE = "clanMate"
ALLOWED_BATTLE_MODES = ["PickMode", "DraftMode", "Draft_Competitive", "ClassicDecks_Friendly", "Duel_1v1_Friendly"]

logger = configured_logger("db.log")

def create_connection(host="localhost", port=3306, user=os.environ.get("MYSQL_USERNAME"), password=os.environ.get("MYSQL_PASSWORD"), database="clash_royale"):
    """
    Creates a connection to the clash_royale database.
    """
    cnx = None
    try:
        cnx = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
    except mysql.connector.Error as e:
        logger.critical(f"Error: {e}")
    except AttributeError as e:
        logger.critical(f"Error: {e}")
    return cnx

def table_exists(cursor, table_name):
    """
    Checks if a table exists in the database. 
    Used in initialize_tables()
    """
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    # print("Tables variable:", tables)
    return any(table_name.lower() == t[0] for t in tables)

def create_table(cursor, table_name, query):
    """
    Creates a table in the database.
    Used in initialize_tables()
    """
    cursor.execute(query)
    logger.info(f"Created table: {table_name}")
    logger.info(f"Query executed: {query}")

def initialize_tables():
    """
    Connects to the clash_royale database and creates tables if they do not exist.
    """
    TABLE_CREATION_QUERIES = {"PLAYERS" : sql.PLAYERS, 
                              "BATTLES" : sql.BATTLES,
                              "SCORES" : sql.SCORES}
    try:
        with create_connection() as cnx:
            with cnx.cursor() as cursor:
                for table_name, query in TABLE_CREATION_QUERIES.items():
                    if table_exists(cursor, table_name):
                        logger.warning(f"Table already exists: {table_name}")
                    else:
                        create_table(cursor, table_name, query)
                logger.info("Tables checked and initialized")
    except mysql.connector.Error as e:
        logger.critical(f"Error: {e}")

def insert_with_error_handling(cnx, query, params, recursive_insertion=False):
    """
    Executes an insert query with parameters and handles errors. If a duplicate entry error occurs and
    `recursive_insertion` is True, the function will retry the insertion with updated parameters by
    recursively calling itself with the remaining parameters.
    """
    try:
        with cnx.cursor() as cursor:
            cursor.executemany(query, params)
            logger.info(f"Query executed: {query}")
            logger.info(f"Parameters: {params}")
            cnx.commit()
    except mysql.connector.IntegrityError as e:
        error_code = e.errno
        if error_code == 1062 and recursive_insertion:
            logger.warning("Duplicate entry found. Retrying with updated parameters")
            return insert_with_error_handling(cnx, query, params[1:], recursive_insertion=True)
        else:
            logger.critical(f"Error: {e}")
            cnx.rollback()
            logger.warning(TX_ROLLBACK_MSG)
    except mysql.connector.Error as e:
        logger.critical(f"Error: {e}")
        cnx.rollback()
        logger.warning(TX_ROLLBACK_MSG)

def select_with_error_handling(cnx, query, params):
    """
    Executes a select query with parameters and error handling. 
    If params is None or empty, no sql statements are executed.
    """
    try:
        with cnx.cursor() as cursor:
            if params is None:
                cursor.execute(query)
                logger.info(f"Query executed: {query}")
            else:
                cursor.execute(query, params)
                logger.info(f"Query executed: {query}")
                logger.info(f"Parameters: {params}")
            result = cursor.fetchall()
            return result
    except mysql.connector.IntegrityError as e:
        logger.critical(f"Error: {e}")
    except mysql.connector.Error as e:
        logger.critical(f"Error: {e}")

def get_player_id_by_name(player_name):
    """
    Retrieves the player ID for a given player_name from the "players" table.
    """
    with create_connection() as cnx:
        query = "SELECT id FROM players WHERE name = %s"
        result = select_with_error_handling(cnx, query, (player_name,))
        if result:
            return result[0][0]
        else:
            return None

def get_player_name_by_id(id):
    """
    Retrieves the player name for a given player id from the "players" table.
    """
    with create_connection() as cnx:
        query = "SELECT name FROM players WHERE id = %s"
        result = select_with_error_handling(cnx, query, (id,))
        if result:
            return result[0][0]
        else:
            return None

def get_player_name_by_tag(player_tag):
    """
    Retrieves the player name for a given tag from the "players" table.
    """
    with create_connection() as cnx:
        query = "SELECT name FROM players WHERE tag = %s"
        result = select_with_error_handling(cnx, query, (player_tag,))
        if result:
            return result[0][0]
        else:
            return None

def get_player_info(player_tag):
    """
    Retrieves all column informations for a given player tag from the "players" table.
    """
    with create_connection() as cnx:
        query = "SELECT * FROM players WHERE tag = %s"
        result = select_with_error_handling(cnx, query, (player_tag,))
        if result:
            column_names = ["id", "tag", "name", "1v1_battle_count", "1v1_win_count", "1v1_three_crowns_win_count"]
            player_info = dict(zip(column_names, result[0]))
            return player_info
        else:
            return None

def get_player_tags():
    """
    Retrieves all tags from the "players" table.
    """
    with create_connection() as cnx:
        query = "SELECT tag FROM players"
        result = select_with_error_handling(cnx, query, ())
        if result:
            return [tag[0] for tag in result]
        else:
            return None

def get_players():
    """
    Retrieves all tags, names etc. from the "players" table.
    """
    with create_connection() as cnx:
        query = "SELECT tag, name, 1v1_battle_count, 1v1_win_count, 1v1_three_crowns_win_count FROM players"
        result = select_with_error_handling(cnx, query, ())
        if result:
            # return result as dict for better readability in template html
            columns = ["tag", "name", "1v1_battle_count", "1v1_win_count", "1v1_three_crowns_win_count"]
            players = [dict(zip(columns, row)) for row in result]
            return players
        else:
            return None

def extract_battles(battles):
    """
    Processes the output of get_battles. Returns a list of dictionaries, containing battle data.
    """
    player_ids = set()

    # Extract player IDs from battles
    for battle_info in battles:
        player_ids.add(battle_info[3])  # Player 1 ID
        player_ids.add(battle_info[10])  # Player 2 ID

    # Fetch player names in a batch
    player_names = {player_id: get_player_name_by_id(player_id) for player_id in player_ids}

    # Process battles with cached player names
    battles_data = [{
        "time": battle_info[0],
        "game_mode": battle_info[1],
        "player1_crowns": battle_info[2],
        "player1_name": player_names.get(battle_info[3], "Unknown"),  # Default to "Unknown" if name not found
        "player1_king_hp": battle_info[4],
        "player1_princess1_hp": battle_info[5],
        "player1_princess2_hp": battle_info[6],
        "player1_elixir_leaked": battle_info[7],
        "player1_deck_string": battle_info[8],
        "player2_crowns": battle_info[9],
        "player2_name": player_names.get(battle_info[10], "Unknown"),
        "player2_king_hp": battle_info[11],
        "player2_princess1_hp": battle_info[12],
        "player2_princess2_hp": battle_info[13],
        "player2_elixir_leaked": battle_info[14],
        "player2_deck_string": battle_info[15],
    } for battle_info in battles]

    return battles_data

def get_query_and_params(latest_battle_time, game_mode, player_tag, enemy_tag, limit):
    """
    Generate a tuple of SQL query and its parameters based on input arguments.
    """
    query_params_dict = {
        # All battles
        (True, True, True, False) : (sql.ALL_BATTLES, ()),
        # All battles with limit
        (True, True, True, True) : (sql.ALL_BATTLES_WITH_LIMIT, (latest_battle_time,)),

        # Battles by game_mode
        (False, True, True, False) : (sql.BATTLES_BY_GAME_MODE, (game_mode,)),
        # Battles by game_mode with limit
        (False, True, True, True) : (sql.BATTLES_BY_GAME_MODE_WITH_LIMIT, (latest_battle_time, game_mode,)),
        
        # player_tag
        (True, False, True, False) : (sql.BATTLES_BY_PLAYER_TAG_NO_LIMIT, (latest_battle_time, player_tag,)),
        # player_tag with limit
        (True, False, True, True) : (sql.BATTLES_BY_PLAYER_TAG, (latest_battle_time, player_tag,)),
        
        
        # player_tag, game_mode 
        (False, False, True, False) : (sql.BATTLES_BY_PLAYER_TAG_BY_GAME_MODE_NO_LIMIT, (latest_battle_time, player_tag, game_mode,)),
        # player_tag, game_mode with limit
        (False, False, True, True) : (sql.BATTLES_BY_PLAYER_TAG_BY_GAME_MODE, (latest_battle_time, player_tag, game_mode,)),
       
        # player_tag, enemy_tag
        (True, False, False, False) : (sql.BATTLES_BY_PLAYER_TAG_BY_ENEMY_TAG_NO_LIMIT, (latest_battle_time, player_tag, enemy_tag)),
        # player_tag, enemy_tag with limit
        (True, False, False, True) : (sql.BATTLES_BY_PLAYER_TAG_BY_ENEMY_TAG, (latest_battle_time, player_tag, enemy_tag)),
        
        # player_tag, game_mode, enemy_tag
        (False, False, False, False) : (sql.BATTLES_BY_PLAYER_TAG_BY_GAME_MODE_BY_ENEMY_TAG_NO_LIMIT, (latest_battle_time, player_tag, enemy_tag, game_mode,)),
        # player_tag, game_mode, enemy_tag with limit
        (False, False, False, True) : (sql.BATTLES_BY_PLAYER_TAG_BY_GAME_MODE_BY_ENEMY_TAG, (latest_battle_time, player_tag, enemy_tag, game_mode,)),
    }
    (query, params) = query_params_dict[(game_mode == "ALL", player_tag is None, enemy_tag is None, limit)]
    return query, params

def get_battles(latest_battle_time="2200-12-31", game_mode="ALL", player_tag=None, enemy_tag=None, limit=True):
    
    """
    Retrieves a list of battle information dictionaries for the given parameters.
    """
    with create_connection() as cnx:
        try:
            with cnx.cursor() as cursor:
                query, params = get_query_and_params(latest_battle_time, game_mode, player_tag, enemy_tag, limit)
                cursor.execute(query, params)
                logger.info(f"Query executed: {query}")
                logger.info(f"Parameters: {params}")
                battles = cursor.fetchall()
                battles_data = extract_battles(battles)
                return battles_data
        except TypeError as e:
            # Example: Error:  403 Client Error: Forbidden for url: https://api.clashroyale.com/v1/players/%23UURVVJQJ/battlelog
            # Authentication failed
            logger.critical("Type Error:", str(e))
        except mysql.connector.Error as e:
            logger.critical("Error:", str(e))

def parse_princess_tower_hp(princess_tower_hp):
    """
    Parses the princess tower HP data and extracts the individual tower HP values.
    """
    princess_tower_hp = ast.literal_eval(princess_tower_hp)
    if princess_tower_hp is None:
        return 0, 0
    elif  len(princess_tower_hp) == 1:
        return princess_tower_hp[0], 0
    else:
        return princess_tower_hp[0], princess_tower_hp[1]

def insert_members():
    """
    Fetches clan members (tag, name) from API, 
    inserts them into the database"s players table.
    """
    clan_members = api.fetch_clan_members()
    with create_connection() as cnx:
        query = "INSERT INTO players (tag, name) VALUES (%s, %s)"
        insert_with_error_handling(cnx, query, clan_members, recursive_insertion=True)

def insert_battle(cursor, battle_info):
    """
    Inserts a battle record into the "battles" table.
    """
    query = "INSERT INTO battles (time, type, game_mode) VALUES (%s, %s, %s)"
    try:
        cursor.execute(query, battle_info[:3])
        return True
    except mysql.connector.Error as e:
        logger.critical(f"Error: {e}")
        return False

def insert_score(cursor, player_data, player_deck, battle_id):
    """
    Inserts a score record into the "scores" table.
    """
    query = """
    INSERT INTO scores (crowns, king_tower_hp, princess_tower_1_hp, princess_tower_2_hp,
                        elixir_leaked, deck_string, battle_id, player_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    name = player_data[0]
    crowns = player_data[1]
    elixir_leaked = player_data[2]
    king_tower_hp = player_data[3]
    princess_tower_1_hp, princess_tower_2_hp = parse_princess_tower_hp(str(player_data[4]))
    player_id = get_player_id_by_name(name)
    try:
        cursor.execute(query, (crowns, king_tower_hp, princess_tower_1_hp, princess_tower_2_hp,
                                   elixir_leaked, player_deck, battle_id, player_id))
    except mysql.connector.Error as e:
        logger.critical(f"Error: {e}")

def check_for_battle_duplicate(time, player1_id, player2_id):
    """
    Check for duplicate battles in the "battles" table based on the provided time,
    player1_id, and player2_id. 
    
    This method is necessary due to a bug in the clash royale system:
    Sometimes the time of battles can differ by 1 second in the battle logs of different players.
    """
    # Prepare datetime variables
    datetime_format = "%Y-%m-%d %H:%M:%S"
    datetime_object = datetime.strptime(time, datetime_format)
    time_plus_1 = datetime_object + timedelta(seconds=1)
    time_plus_1 = iso8601_to_datetime(str(time_plus_1), datetime_format)
    time_minus_1 = datetime_object - timedelta(seconds=1)
    time_minus_1 = iso8601_to_datetime(str(time_minus_1), datetime_format)
    # Query
    with create_connection() as cnx:
        query = sql.BATTLE_QUERY_FOR_DUPLICATION_CHECK
        query = query.format(time_plus_1, time_minus_1)
        result = select_with_error_handling(cnx, query, None)
        if result:
            player1_idx = result[0][3]
            player2_idx = result[0][10]
            if (player1_id == player1_idx or player1_id == player2_idx) and (player2_id == player1_idx or player2_id == player2_idx):
                logger.critical("Duplicate found. Insertion of battle and scores will be aborted for this battle.")
                return True
        return False

def insert_new_battles():
    """
    Inserts new battles into the system. Skips battles that are already in the database.

    Retrieves player tags, fetches battles for each player, and inserts the battles and scores into the 
    corresponding table.
    """
    player_tags = get_player_tags()
    for player_tag in player_tags:
        battles = api.fetch_battle_log(player_tag)
        # if api key doesn"t allow current ip addr, then battles will have the error: TypeError: "NoneType" object is not iterable
        for battle in battles:
            battle_info = battle[0]
            if not (battle_info[1] == ALLOWED_BATTLE_TYPE and battle_info[2] in ALLOWED_BATTLE_MODES):
                logger.warning("Battle type or game mode not allowed")
                continue
            
            time = battle_info[0]
            player1_data = battle[1][0]
            player1_deck = str(battle[2])
            player2_data = battle[3][0]
            player2_deck = str(battle[4])
            player1_id = get_player_id_by_name(player1_data[0])
            player2_id = get_player_id_by_name(player2_data[0])
            found_duplicate = check_for_battle_duplicate(time, player1_id, player2_id)
            
            if found_duplicate:
                continue

            with create_connection() as cnx:
                with cnx.cursor() as cursor:
                    cnx.start_transaction()
                    success = insert_battle(cursor, battle_info)
                    
                    if success:
                        battle_id = cursor.lastrowid
                        insert_score(cursor, player1_data, player1_deck, battle_id)
                        insert_score(cursor, player2_data, player2_deck, battle_id)
                        cnx.commit()
                        logger.info(f"Inserted battle with the id:{battle_id} and the corresponding scores")
                    else:
                        cnx.rollback()
                        logger.warning(TX_ROLLBACK_MSG)

def update_player_infos():
    """
    Updates the columns "1v1_battle_count", "1v1_win_count" and "1v1_three_crowns_win_count" 
    for all players in the "players" table by calculating them from the retrieved data
    battles data from the database.
    """
    player_tags = get_player_tags()
    with create_connection() as cnx:
        try:
            for player_tag in player_tags:
                battles = get_battles(player_tag=player_tag, limit=False)
                battle_count_1v1 = len(battles)
                win_count_1v1 = 0
                three_crowns_win_count_1v1 = 0

                for battle in battles:
                    player_crowns = battle["player1_crowns"]
                    enemy_crowns = battle["player2_crowns"]

                    if player_crowns > enemy_crowns:
                        win_count_1v1 += 1

                        if player_crowns == 3:
                            three_crowns_win_count_1v1 += 1
                
                with cnx.cursor() as cursor:
                    params = (battle_count_1v1, win_count_1v1, three_crowns_win_count_1v1, player_tag)
                    query = """UPDATE players 
                    SET 1v1_battle_count = %s, 1v1_win_count = %s, 1v1_three_crowns_win_count = %s 
                    WHERE tag = %s"""
                    cursor.execute(query, params)
                    logger.info(f"Query executed: {query}")
                    logger.info(f"Parameters: {params}")
                cnx.commit()
                logger.info("Updated the columns battle_count, 1v1_win_count and 1v1_three_crowns_win_count for all players")
        except TypeError as e:
            # Example: Error:  403 Client Error: Forbidden for url: https://api.clashroyale.com/v1/players/%23UURVVJQJ/battlelog
            # Authentication failed
            logger.critical("Type Error:", str(e))
            cnx.rollback()
            logger.warning(TX_ROLLBACK_MSG)
        except mysql.connector.Error as e:
            logger.critical("Error:", str(e))
            cnx.rollback()
            logger.warning(TX_ROLLBACK_MSG)
    
def stats_versus(player_tag1, player_tag2, game_mode="ALL"):
    """
    Calculate and return statistics for battles between two players in a specified game mode.
    """
    battles = get_battles(game_mode=game_mode, player_tag=player_tag1, enemy_tag=player_tag2, limit=False)
    
    battle_count = len(battles)
    win_count = 0
    three_crowns_win_count = 0
    
    for battle in battles:
        player1_crowns = battle["player1_crowns"]
        player2_crowns = battle["player2_crowns"]
        
        if player1_crowns > player2_crowns:
            win_count += 1
            if player1_crowns >= 3:
                three_crowns_win_count += 1

    win_rate = round((win_count / battle_count) * 100, 2) if battle_count > 0 else 0

    # Return the result as a dictionary
    return {
        "win_rate": win_rate,
        "battle_count": battle_count,
        "win_count": win_count,
        "three_crowns_win_count": three_crowns_win_count
    }
 
def main():
    # initialize_tables()
    # insert_members()
    insert_new_battles()
    update_player_infos()
                 
if __name__ == "__main__":
    main()
