import hexutil
import logging


class Area(object):
    def __init__(self, name, owner, dice, neighbours, hexes):
        self.logger = logging.getLogger('CLIENT')

        self.name = int(name)
        self.owner_name = int(owner)
        self.dice = int(dice)
        self.neighbours = [int(n) for n in neighbours]
        self.hexes = [[int(i) for i in h] for h in hexes]

    def get_adjacent_areas(self):
        return self.neighbours

    def get_dice(self):
        return self.dice

    def get_name(self):
        return self.name

    def get_owner_name(self):
        return self.owner_name

    def has_dice(self):
        return self.dice >= 2

    def set_dice(self, dice):
        self.dice = dice
        if dice < 1 or dice > 8:
            self.logger.error("Area {0} dice set to {1}.".format(self.name, dice))

    def set_owner(self, name):
        self.owner_name = int(name)

    ##############
    # UI METHODS #
    ##############
    def get_hexes(self):
        return [hexutil.Hex(h[0], h[1]) for h in self.hexes]
