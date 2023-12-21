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
    Fetches and returns the battle log of a player.
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
