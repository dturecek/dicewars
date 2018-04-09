class Player(object):
    def __init__(self, name, score):
        self.name = int(name)
        self.score = int(score)

        self.areas = []
        self.areas_not_full = []
        self.activated = False
        self.dice_reserve = 0

    def activate(self):
        self.activated = True

    def deactivate(self):
        self.activated = False

    def get_name(self):
        return self.name

    def get_reserve(self):
        return self.dice_reserve

    def get_score(self):
        return self.score

    def remove_area(self, area):
        self.areas.remove(area)
        if area in self.areas_not_full:
            self.areas_not_full.remove(area)

    def set_reserve(self, dice):
        self.dice_reserve = dice

    def set_score(self, score):
        self.score = score
