import random


class Character:
    def __init__(self, hp, dmg):
        self.max_hp = hp
        self.hp = hp
        self.dmg = dmg

    def is_dead(self):
        return self.hp <= 0

    def character_dmg(self):
        return random.randint(1, self.dmg)

    def __str__(self):
        return self.__class__.__name__

    def display_statistics_characters(self):
        msg = ""
        msg += "The {} --> Stats: {}HP and {}DMG.".format(self.__class__.__name__, self.hp, self.dmg) + "\n"
        return msg


class Bookworm(Character):
    pass


class Worker(Character):
    pass


class Procrastinator(Character):
    pass


class Whatsapper(Character):
    pass
