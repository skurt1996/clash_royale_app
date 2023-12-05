"""
This module is responsible for retrieving data from the clash royale API.
Module is used by db.py to write retrieved data to the database.
"""
import os
from datetime import datetime

import requests

from utils import iso8601_to_datetime

API_TOKEN = os.environ.get("CLASH_ROYALE_API_TOKEN")
API_URL = "https://api.clashroyale.com/v1"
HEADERS = {"Authorization": "Bearer " + API_TOKEN}

CLAN_TAG = "#LGV2LVQY" # Clan: Retire
PLAYER_TAG = "#2J200GLG8" # Spieler: Raue Hände

def fetch_clan_members(clan_tag=CLAN_TAG):
    """
    Fetches and returns the members of a clan from the API.

    Args:
        clan_tag (str): The clan"s tag. Defaults to CLAN_TAG.

    Returns:
        list: A list of tuples representing the clan members. Each tuple contains the member"s tag, name.
    """
    END_POINT = "/clans/%23" + clan_tag[1:] + "/members"
    clan_members = []
    try:
        with requests.get(API_URL + END_POINT, headers=HEADERS) as response:
            response.raise_for_status()
            json_data = response.json()
            clan_members = [(item["tag"], item["name"]) for item in json_data["items"]]
            return clan_members
    except requests.exceptions.RequestException  as e:
        print("Error: ", str(e))

def fetch_battle_log(player_tag=PLAYER_TAG):
    """
    Fetches and return the battle log of a player.

    Args:
        player_tag (str): The player"s tag. Defaults to PLAYER_TAG.

    Returns:
        list: A list of battles, each represented as a tuple containing the following information:
            - battle_info (tuple): Information about the battle, including battle time, type, and game mode.
            - team_info (list): Information about the player"s team, including name, crowns, elixir leaked, king tower hit points, and princess towers hit points.
            - player_info (list): Information about the player, including name, crowns, elixir leaked, king tower hit points, and princess towers hit points.
            - opponent_info (list): Information about the opponent, including name, crowns, elixir leaked, king tower hit points, and princess towers hit points.
            - player_deck (list): The player"s deck, represented as a list of card names.
            - opponent_deck (list): The opponent"s deck, represented as a list of card names.
    """
    END_POINT = "/players/%23" + player_tag[1:] + "/battlelog"
    try:
        with requests.get(API_URL + END_POINT, headers=HEADERS) as response:
            response.raise_for_status()
            match_data = response.json()
            battles = []
            for battle in match_data:
                 battle_info = (
                     iso8601_to_datetime(battle["battleTime"], "%Y%m%dT%H%M%S.%fZ"),
                     battle["type"], 
                     battle["gameMode"]["name"]
                 )
                 player_info = [
                     (
                         it["name"],
                         it["crowns"],
                         it["elixirLeaked"],
                         it["kingTowerHitPoints"],
                         it["princessTowersHitPoints"]
                     ) for it in battle["team"]]   
                 opponent_info = [
                     (
                         it["name"],
                         it["crowns"], 
                         it["elixirLeaked"], 
                         it["kingTowerHitPoints"], 
                         it["princessTowersHitPoints"]
                     ) for it in battle["opponent"]
                 ]
                 player_deck = [card["name"] for card in battle["team"][0]["cards"]]
                 opponent_deck = [card["name"] for card in battle["opponent"][0]["cards"]]
                 battles.append((battle_info, player_info, player_deck, opponent_info, opponent_deck))
        return battles
    except requests.exceptions.RequestException  as e:
        print("Error: ", str(e))

    
def main():
    print(fetch_battle_log())


if __name__ == "__main__":
    main()
