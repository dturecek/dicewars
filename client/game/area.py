import hexutil
import logging


class Area(object):
    """Game board area
    """
    def __init__(self, name, owner, dice, neighbours, hexes):
        """
        Parameters
        ----------
        name : int
        owner : int
        dice : int
        neighbours : list of int
        hexes : list of list of int
            Hex coordinates of for all Area's hexes
        """
        self.logger = logging.getLogger('CLIENT')

        self.name = int(name)
        self.owner_name = int(owner)
        self.dice = int(dice)
        self.neighbours = [int(n) for n in neighbours]
        self.hexes = [[int(i) for i in h] for h in hexes]

    def get_adjacent_areas(self):
        """Return names of adjacent areas
        """
        return self.neighbours

    def get_dice(self):
        """Return number of dice in the Area
        """
        return self.dice

    def get_name(self):
        """Return Area's name
        """
        return self.name

    def get_owner_name(self):
        """Return Area's owner's name
        """
        return self.owner_name

    def has_dice(self):
        """Return True if area has enough dice to attack
        """
        return self.dice >= 2

    def set_dice(self, dice):
        """Set area's dice
        """
        self.dice = dice
        if dice < 1 or dice > 8:
            self.logger.error("Area {0} dice set to {1}.".format(self.name, dice))

    def set_owner(self, name):
        """Set owner name
        """
        self.owner_name = int(name)

    ##############
    # UI METHODS #
    ##############
    def get_hexes(self):
        """Return Hex objects of the Area
        """
        return [hexutil.Hex(h[0], h[1]) for h in self.hexes]
