import logging

from game.area import Area


class Board(object):
    """Game board
    """
    def __init__(self, areas, board):
        """
        Parameters
        ----------
        areas : dict of int: list of int
            Dictionary of game areas and their neighbours
        board : dict
            Dictionary describing the game's board
        """
        self.logger = logging.getLogger('CLIENT')
        self.areas = {}
        for area in areas:
            self.areas[area] = Area(area, areas[area]['owner'], areas[area]['dice'],
                                    board[area]['neighbours'], board[area]['hexes'])

    def get_area(self, idx):
        """Get Area given its name
        """
        return self.areas[str(idx)]

    def get_player_dice(self, player):
        """Get all dice of a single player
        """
        dice = 0
        for area in self.areas.values():
            if area.get_owner_name() == player:
                dice += area.get_dice()
        return dice
