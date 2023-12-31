"""
In this module forms for our HTML templates are defined.
"""

from flask_wtf import FlaskForm
from wtforms import SelectField

class GameModeSelection(FlaskForm):
    # Form to select game mode
    game_mode_selection = SelectField('game_mode', choices= [
        ("ALL", "Alle Kampfmodi"),
        ("Draft_Competitive", "Dreifach-Auswahlkampf"),
        ("PickMode", "Mega-Auswahlherausforderung"),
        ("ClassicDecks_Friendly", "Klassikdeck-Kampf"),
        ("DraftMode", "Auswahlkampf"),
        ("Duel_1v1_Friendly", "Duell"),
    ])

class GameModeEnemySelection(GameModeSelection):
    # Form to select game mode and enemy
    # Choices to be set in /player routing method in run.py
    enemy_selection = SelectField('enemy', choices =[])
