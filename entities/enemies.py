import random


class Enemy:
    def __init__(self, hp, dmg):
        self.max_hp = hp
        self.dmg = dmg
        self.hp = hp

    def is_dead(self):
        return self.hp <= 0

    def enemy_dmg(self):
        return random.randint(1, self.dmg)

    def __str__(self):
        return self.__class__.__name__

    def display_statistics_enemies(self):
        msg = ""
        msg += "{} --> Stats: {}HP and {}DMG.".format(self.__class__.__name__, self.hp, self.dmg) + "\n"
        return msg


class PartialExam(Enemy):
    pass


class FinalExam(Enemy):
    pass


class TheoreticalClass(Enemy):
    pass


class Teacher(Enemy):
    def enemy_dmg(self):
        dmg = random.randint(1, self.dmg)
        if dmg == 7:
            return dmg * 2
        else:
            return dmg







