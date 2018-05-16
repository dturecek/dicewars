class Player(object):
    """Representation of a single player
    """
    def __init__(self, name, score):
        """
        Parameters
        ----------
        name : int
            Player's name
        score : int
            Initial score

        Attributes
        ----------
        dice_reserve : int
        """

        self.name = int(name)
        self.score = int(score)
        self.dice_reserve = 0
        self.activated = False

    def get_name(self):
        return self.name

    def get_reserve(self):
        return self.dice_reserve

    def get_score(self):
        return self.score

    def set_reserve(self, dice):
        self.dice_reserve = dice

    def set_score(self, score):
        self.score = score

    def activate(self):
        self.activated = True

    def deactivate(self):
        self.activated = False

 
