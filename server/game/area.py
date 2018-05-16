import logging


class Area(object):
    """Object representing a single area.
    """
    def __init__(self, name, adjacent_areas):
        """ 
        Parameters
        ----------
        name : int
            Identifier of the area
        adjacent_areas : list of int
            Names of adjacent areas

        Attributes
        ----------
        adjacent_areas : list of Area
            Adjacent areas
        adjacent_areas_names : list of int
            Names of adjacent areas
        dice : int
            Number of dice in the area
        owner_name : int
            Name of the player controlling the area
        """
        self.name = name
        self.adjacent_areas_names = adjacent_areas
        self.logger = logging.getLogger('SERVER')

        self.adjacent_areas = []
        self.dice = 0
        self.owner_name = None

    def add_adjacent_areas(self, board):
        """Add instances of adjacent areas to the list

        Parameters
        ----------
        board : Board
            Instance of the Board class
        """
        for name in self.adjacent_areas_names:
            self.adjacent_areas.append(board.areas[name])

    def add_die(self):
        """Add die to area's dice

        Returns
        -------
        bool
            False if area already contains 8 dice, otherwise True
        """
        if self.dice >= 8:
            self.dice = 8
            return False
        else:
            self.dice += 1
            return True

    def get_adjacent_areas(self):
        """Get list of adjacent areas

        Returns
        -------
        list of Area
            Adjacent areas
        """
        return self.adjacent_areas

    def get_adjacent_areas_names(self):
        """Get list of adjacent areas' names

        Returns
        -------
        list of int
            Names of adjacent areas
        """
        return self.adjacent_areas_names

    def get_dice(self):
        """Get number of dice

        Returns
        -------
        int
            Number of dice
        """
        return self.dice

    def get_name(self):
        """Get area's name

        Returns
        -------
        int 
            Identifier of the area
        """
        return self.name

    def get_owner_name(self):
        """Get owner's name
        
        Returns
        -------
        int or bool
            Returns owner's name if area has an owner, otherwise False
        """
        if not self.owner_name:
            return False
        else:
            return self.owner_name

    def set_dice(self, dice):
        """Set area's dice to a certain value
        
        Parameters
        ----------
        dice : int
            Number of dice
        """
        if dice < 1 or dice > 8:
            self.logger.warning("Trying to assign {0} dice to area {1}"\
                                .format(dice, self.name))
        else:
            self.dice = dice

    def set_owner_name(self, name):
        """Set owner's name

        Parameters
        ----------
        name : int
            Name of the owner
        """
        self.owner_name = name
