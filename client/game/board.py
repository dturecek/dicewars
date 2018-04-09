import logging

from game.area import Area


class Board(object):
    def __init__(self, areas, board, players):
        self.logger = logging.getLogger('CLIENT')
        self.areas = {}
        for area in areas:
            self.areas[area] = Area(area, areas[area]['owner'], areas[area]['dice'],
                                    board[area]['neighbours'], board[area]['hexes'])

    def get_area(self, idx):
        return self.areas[str(idx)]
