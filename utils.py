"""
This module contains some utility functions.
"""

from datetime import datetime
import ast
import os

def iso8601_to_datetime(iso8601_date, datetime_format):
    """
    Converts an ISO 8601 formatted date string to a datetime object and returns it.
    """
    return str(datetime.strptime(iso8601_date, datetime_format))

def replace_card_names_by_img_path(deck_string):
    """
    Given a deck string containing a list of card names, this function replaces each card name
    with a corresponding image path while applying lowercase, space-to-underscore, and character removal transformations.
    """
    deck_list = ast.literal_eval(deck_string)
    deck_list = ["/static/images/cards/" + card.lower().replace(" ", "_").replace("'", "").replace("[", "").replace("]", "") + ".webp" for card in deck_list]
    return deck_list

def initialize_cards_data(card_files):
    """
    Initializes a list of card data dictionaries based on a list of card files and returns it.
    """
    cards_data = []
    for card_file in card_files:
        card_name = os.path.splitext(card_file)[0].replace("_", " ").title()
        cards_data.append({"image": card_file, "name": card_name, "battle_count": 0, "win_count": 0})
    return cards_data

def update_cards_data_stats(battles_data, cards_data):
    """
    Updates the battle and win counts in the cards_data based on battles_data.
    """
    for battle in battles_data:
        player1_deck_list = ast.literal_eval(battle["player1_deck_string"])
        player2_deck_list = ast.literal_eval(battle["player2_deck_string"])

        update_battle_count(player1_deck_list + player2_deck_list, cards_data)

        if battle["player1_crowns"] > battle["player2_crowns"]:
            update_win_count(player1_deck_list, cards_data)
        elif battle["player2_crowns"] > battle["player1_crowns"]:
            update_win_count(player2_deck_list, cards_data)

def update_battle_count(deck_list, cards_data):
    """
    Update the battle count in cards_data based on the given deck_list.
    """
    for card_name in deck_list:
        for card_data in cards_data:
            if card_data["name"] == card_name:
                card_data["battle_count"] += 1

def update_win_count(winning_deck_list, cards_data):
    """
    Update the win count in cards_data based on the given winning_deck_list.
    """
    for card_name in winning_deck_list:
        for card_data in cards_data:
            if card_data["name"] == card_name:
                card_data["win_count"] += 1
