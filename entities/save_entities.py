import json

import entities_dicts as dc
import characters as ch
import enemies as en


def list_loop(lt, s):
    for i in range(len(lt)):
        s.append({"class": lt[i].__str__(),
                  "HP": lt[i].hp})
    return s


# SAVE AND WRITE THE DICTIONARY AS STRING
def saved_json(list_players, list_enemies, ns, cs, ct):
    players = []
    enemies = []
    players = list_loop(list_players, players)
    enemies = list_loop(list_enemies, enemies)
    game = {"stages": ns,
            "current_stage": cs,
            "current_turn": ct,
            "enemies": enemies}
    dictionary = {"players": players,
                  "game": game}
    saved_string = json.dumps(dictionary)
    return saved_string


# LOAD AND READ THE STRING AS DICTIONARY
def load_json(file, list_players, list_enemies, dict_game):
    with open(file, 'r') as f:
        saved_dict = json.load(f)
    # DICTIONARY KEY - "PLAYERS":
    saved_dict_players = saved_dict["players"]
    # DICTIONARY KEY - "GAME":
    saved_dict_game = saved_dict["game"]

    saved_dict_enemies = saved_dict_game["enemies"]
    saved_dict_n_s = saved_dict_game["stages"]
    saved_dict_c_s = saved_dict_game["current_stage"]
    saved_dict_c_t = saved_dict_game["current_turn"]
    # KEY - "PLAYERS":
    for i in range(len(saved_dict_players)):
        if saved_dict_players[i]["class"] == "Bookworm":
            character = ch.Bookworm(saved_dict_players[i]["HP"], dc.b["DMG"])
        elif saved_dict_players[i]["class"] == "Worker":
            character = ch.Worker(saved_dict_players[i]["HP"], dc.w["DMG"])
        elif saved_dict_players[i]["class"] == "Procrastinator":
            character = ch.Procrastinator(saved_dict_players[i]["HP"], dc.p["DMG"])
        else:
            character = ch.Whatsapper(saved_dict_players[i]["HP"], dc.wh["DMG"])
        list_players.append(character)  # ADD TO THE LIST OF CURRENT CHARACTERS
    # KEY - "ENEMIES":
    for i in range(len(saved_dict_enemies)):
        if saved_dict_enemies[i]["class"] == "PartialExam":
            enemy = en.PartialExam(saved_dict_enemies[i]["HP"], dc.pe["DMG"])
        elif saved_dict_enemies[i]["class"] == "FinalExam":
            enemy = en.FinalExam(saved_dict_enemies[i]["HP"], dc.fe["DMG"])
        elif saved_dict_enemies[i]["class"] == "TheoreticalClass":
            enemy = en.TheoreticalClass(saved_dict_enemies[i]["HP"], dc.th["DMG"])
        else:
            enemy = en.Teacher(saved_dict_enemies[i]["HP"], dc.t["DMG"])
        list_enemies.append(enemy)  # ADD TO THE LIST OF CURRENT ENEMIES
    dict_game["stages"] = saved_dict_n_s
    dict_game["current_stage"] = saved_dict_c_s
    dict_game["current_turn"] = saved_dict_c_t
