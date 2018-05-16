from game.area import Area


class Board(object):
    """Object representing the game board
    """
    def __init__(self, board):
        """
        Parameters
        ----------
        board : dict of int: list of int
            Dictionary listing adjacent areas for each area

        Attributes
        ----------
        areas : dict of int: Area
            Dictionary of Area instances
        """
        self.board = board
        self.areas = {}
        for area in board:
            self.areas[area] = Area(area, board[area]['neighbours'])
        for a in self.areas:
            self.areas[a].add_adjacent_areas(self)

    def get_area_by_name(self, name):
        """Get instance of Area by its name

        Parameters
        ----------
        name : int
            Area's name

        Returns
        -------
        Area
            Instance of an area
        """
        for a in self.areas:
            if name == self.areas[a].get_name():
                return self.areas[a]

    def get_board(self):
        """Get dictionary listing adjacent areas for each area
        
        Returns
        -------
        dictionary of int: list of int
        """
        return self.board

    def get_number_of_areas(self):
        """Get number of areas in the game

        Returns
        -------
        int
        """
        return len(self.areas)
