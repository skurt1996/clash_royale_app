import os

from flask import Flask, render_template, abort, request, jsonify

from db import get_players, get_player_name_by_tag, get_battles, get_player_info, stats_versus
from utils import replace_card_names_by_img_path, initialize_cards_data, update_cards_data_stats
from forms import GameModeSelection, GameModeEnemySelection

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/players", methods=["GET"])
def players():
    return render_template("players.html", players=get_players())

@app.route("/player/<string:player_tag>", methods=["GET", "POST"])
def player(player_tag):
    player_name = get_player_name_by_tag(player_tag)
    if player_name is None:
        abort(404, description="Player not found.")
    
    form = GameModeEnemySelection()
    form.enemy_selection.choices = [("None", "Alle Gegner")] + [(player["tag"], player["name"]) for player in get_players() if player["tag"] != player_tag]
    
    player_info = get_player_info(player_tag)
    battles_data = []
    
    if request.method == "POST":
        if form.enemy_selection.data == "None":
            form.enemy_selection.data = None
            
        battles_data = get_battles(game_mode=form.game_mode_selection.data,
                                   player_tag=player_tag,
                                   enemy_tag=form.enemy_selection.data)
        
        stats_data = stats_versus(player_tag, 
                                  player_tag2=form.enemy_selection.data, 
                                  game_mode=form.game_mode_selection.data)
    else:
        battles_data = get_battles(player_tag=player_tag)
        win_rate = round((player_info["1v1_win_count"] / player_info["1v1_battle_count"]) * 100, 2) if player_info["1v1_battle_count"] > 0 else 0
        stats_data = {
            "win_rate": win_rate,
            "battle_count": player_info["1v1_battle_count"],
            "win_count": player_info["1v1_win_count"],
            "three_crowns_win_count": player_info["1v1_three_crowns_win_count"]
        }
    for battle in battles_data:
        battle["player1_deck_string"] = replace_card_names_by_img_path(battle["player1_deck_string"])
        battle["player2_deck_string"] = replace_card_names_by_img_path(battle["player2_deck_string"])
    
    return render_template("player.html",
                           form=form,
                           player_info=player_info,
                           battles_data=battles_data,
                           stats_data=stats_data)

@app.route("/battles", methods=["GET", "POST"])
def battles():
    form = GameModeSelection()
    battles_data = []
    
    if request.method == "POST":
        battles_data = get_battles(game_mode=form.game_mode_selection.data)
    else:
        battles_data = get_battles()
        
    for battle in battles_data:
        battle["player1_deck_string"] = replace_card_names_by_img_path(battle["player1_deck_string"])
        battle["player2_deck_string"] = replace_card_names_by_img_path(battle["player2_deck_string"])
        
    return render_template("battles.html",
                           form=form,
                           battles_data=battles_data) 

@app.route("/api/next_battles", methods=["GET"])
def next_battles():
    latest_battle_time = request.args.get("battle-time")
    
    if not latest_battle_time:
        return jsonify(error="Missing battle-time parameter"), 400
    
    player_tag = request.args.get("player-tag")
    game_mode_selection = request.args.get("game-mode-selection")
    enemy_selection = request.args.get("enemy-selection") # also a tag like player_tag
    
    if enemy_selection == "None":
        enemy_selection = None

    if player_tag:
        battles_data = get_battles(player_tag=player_tag, latest_battle_time=latest_battle_time, game_mode=game_mode_selection, enemy_tag=enemy_selection)
    else:
        battles_data = get_battles(latest_battle_time, game_mode=game_mode_selection)

    if battles_data:
        return jsonify(battles_data)
    else:
        return jsonify(message="No more battles to fetch.")


@app.route("/cards", methods=["GET", "POST"])
def cards():
    form = GameModeSelection()
    
    cards_path = r"C:\Users\samca\Documents\d\clash_royale_app\static\images\cards"
    card_files = os.listdir(cards_path)
    cards_data = initialize_cards_data(card_files)
    
    if request.method == "POST":
        battles_data = get_battles(game_mode=form.game_mode_selection.data, limit=False)
    else:
        battles_data = get_battles(limit=False)
    
    update_cards_data_stats(battles_data, cards_data)

    return render_template("cards.html", form=form, cards_data=cards_data)
    

@app.route("/ranking", methods=["GET"])
def ranking():
    return render_template("ranking.html")

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html", description=error.description), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
