import sys
import os
import random

sys.path.append(os.path.join(os.path.dirname(__file__), "entities"))

import constants as ct
from entities import entities_dicts as dc
from entities import characters as ch
from entities import enemies as en
from entities import save_entities as s

available_characters_all = [ch.Bookworm(dc.b["HP"], dc.b["DMG"]), ch.Worker(dc.w["HP"], dc.w["DMG"]),
                            ch.Procrastinator(dc.p["HP"], dc.p["DMG"]), ch.Whatsapper(dc.wh["HP"], dc.wh["DMG"])]
available_enemies_all = [en.PartialExam(dc.pe["HP"], dc.pe["DMG"]), (en.FinalExam(dc.fe["HP"], dc.fe["DMG"])),
                         en.TheoreticalClass(dc.th["HP"], dc.th["DMG"]), en.Teacher(dc.t["HP"], dc.t["DMG"])]
available_enemies = [en.PartialExam(dc.pe["HP"], dc.pe["DMG"]), en.TheoreticalClass(dc.th["HP"], dc.th["DMG"]),
                     en.Teacher(dc.t["HP"], dc.t["DMG"])]


class Player:
    def __init__(self, name, c_a):
        self.name = name
        self.c_a = c_a

    def __str__(self):
        return self.name

    def __eq__(self, element):
        if str(element):
            return self.name == element
        else:
            return self.c_a == element
        
class Game:
    def __init__(self, stages):
        self.stages = stages
        self.dead_players = 0
        self.current_stage = 1
        self.current_turn = 0
        self.current_characters = []
        self.current_enemies = []
        self.current_game = {}
        self.nickname = []
        self.sockets = []

    def load_game(self, file):
        s.load_json(file, self.current_characters, self.current_enemies, self.current_game)
        self.stages = self.current_game["stages"]
        self.current_stage = self.current_game["current_stage"]
        self.current_turn = self.current_game["current_turn"]

    # PLAYERS TURN
    @staticmethod
    def msg_players_turn():
        msg = ""
        msg += "        ------------------------\n"
        msg += "        -     PLAYERS TURN     -\n"
        msg += "        ------------------------\n"
        return msg

    # MONSTERS TURN
    @staticmethod
    def msg_monsters_turn():
        msg = ""
        msg += "        ------------------------\n"
        msg += "        -     MONSTERS TURN    -\n"
        msg += "        ------------------------\n"
        return msg

    # MENU - AVAILABLE CHARACTERS
    @staticmethod
    def msg_available_character_menu():
        msg = "\n"
        msg += "******** AVAILABLE CHARACTERS ***********\n"
        for c in range(len(available_characters_all)):
            ac = available_characters_all[c]
            msg += str(c + 1) + ".- "
            msg += ac.display_statistics_characters()
        msg += "*****************************************\n"
        return msg

    def msg_current_character_menu(self):
        msg = ""
        msg += "\n*****************************************\n"
        for c in range(len(self.current_characters)):
            cc = self.current_characters[c]
            if not cc.is_dead():
                msg += str(c + 1) + ".- "
                msg += cc.display_statistics_characters()
        msg += "*****************************************\n"
        return msg

    # ADD THE ENEMY IN THE LIST OF CURRENT ENEMIES
    def add_enemy(self, name_enemy):
        if name_enemy == "PartialExam":
            enemy = en.PartialExam(dc.pe["HP"], dc.pe["DMG"])
        elif name_enemy == "FinalExam":
            enemy = en.FinalExam(dc.fe["HP"], dc.fe["DMG"])
        elif name_enemy == "TheoreticalClass":
            enemy = en.TheoreticalClass(dc.th["HP"], dc.th["DMG"])
        else:
            enemy = en.Teacher(dc.t["HP"], dc.t["DMG"])
        self.current_enemies.append(enemy)

    def add_character(self, number_character):
        if number_character == 1:
            character = ch.Bookworm(dc.b["HP"], dc.b["DMG"])
        elif number_character == 2:
            character = ch.Worker(dc.w["HP"], dc.w["DMG"])
        elif number_character == 3:
            character = ch.Procrastinator(dc.p["HP"], dc.p["DMG"])
        else:
            character = ch.Whatsapper(dc.wh["HP"], dc.wh["DMG"])
        self.current_characters.append(character)

    # CREATE THE RANDOM ENEMIES OF THE ROUND
    def create_enemies(self):
        num_partials = 0
        if len(self.current_enemies) <= 0:
            for i in range(ct.n_enemies):
                if self.current_stage <= 3:
                    random_enemy = random.choice(available_enemies)
                else:
                    random_enemy = random.choice(available_enemies_all)
                self.add_enemy(random_enemy.__str__())
                if random_enemy.__str__() == "PartialExam":
                    num_partials = num_partials + 1
            if num_partials == 3:
                random_enemy = random.choice(available_enemies)
                if random_enemy.__str__() == "PartialExam":
                    self.add_enemy(random_enemy.__str__())

    # MENU - CURRENT STAGE
    def msg_current_stage_menu(self):
        msg = ""
        msg += "        *************************\n"
        msg += "        *"
        msg += "        STAGE " + str(self.current_stage) + ""
        msg += "        *\n"
        msg += "        ************************\n"
        msg += "        --- CURRENT MONSTERS ---    \n"
        msg += "*****************************************\n"
        for i in range(len(self.current_enemies)):
            msg += self.current_enemies[i].display_statistics_enemies()
        msg += self.msg_players_turn()
        return msg

    def msg_players_attack(self, c, p):
        msg = ""
        random_enemy = random.choice(self.current_enemies)
        pos_enemy = self.current_enemies.index(random_enemy)
        dmg = c.character_dmg()
        random_enemy.hp = random_enemy.hp - dmg
        self.current_enemies[pos_enemy] = random_enemy
        msg += "The " + str(c) + " (Player: "
        msg += str(self.nickname[p])
        msg += ") did "
        msg += str(dmg)
        msg += " damage to " + str(random_enemy) + ". "
        if random_enemy.is_dead():
            self.current_enemies.remove(random_enemy)
            msg += "The " + str(random_enemy) + " has died. \n"
        return msg

    # ENEMY´S ROUND
    def msg_enemies_attack(self):
        msg = ""
        msg += self.msg_monsters_turn()
        for e in self.current_enemies:
            correct_input = False
            while not correct_input and not self.all_characters_dead():
                random_character = random.choice(self.current_characters)
                pos_character = self.current_characters.index(random_character)
                if not random_character.is_dead():
                    if e.__str__() == "TheoreticalClass":
                        dmg = e.enemy_dmg() + self.current_stage
                    else:
                        dmg = e.enemy_dmg()
                    random_character.hp -= dmg
                    msg += "The " + str(e) + " did "
                    msg += str(dmg)
                    msg += " damage to " + str(random_character) + " (Player: "
                    msg += str(self.nickname[pos_character])
                    msg += "). "
                    if random_character.hp <= 0:
                        self.dead_players += 1
                        random_character.hp = 0
                        msg += str(self.nickname[pos_character]) + " has died. \n"
                    else:
                        msg += "The " + str(random_character) + " has "
                        msg += str(random_character.hp)
                        msg += " left. \n"
                    self.current_characters[pos_character] = random_character
                    correct_input = True
        return msg

    def all_characters_dead(self):
        all_dead = True
        for c in self.current_characters:
            all_dead = all_dead and c.is_dead()
        return all_dead

    def all_enemies_dead(self):
        all_dead = True
        for e in self.current_enemies:
            all_dead = all_dead and e.is_dead()
        return all_dead

    # ADD CHARACTER´S HP AT THE FINAL OF THE ROUND
    def add_hp_round(self):
        for c in self.current_characters:
            if not (c.is_dead()):
                c.hp = int(1.25 * c.hp)
                if c.hp >= c.max_hp:
                    c.hp = c.max_hp
