from game.area import Area


class Board(object):
    def __init__(self, board):
        self.board = board
        self.areas = {}
        for area in board:
            self.areas[area] = Area(area, board[area]['neighbours'])
        for a in self.areas:
            self.areas[a].add_adjacent_areas(self)

    def get_area_by_name(self, name):
        for a in self.areas:
            if name == self.areas[a].get_name():
                return self.areas[a]

    def get_board(self):
        return self.board

    def get_number_of_areas(self):
        return len(self.areas)
