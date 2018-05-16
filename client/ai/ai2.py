from random import shuffle

from ai import GenericAI


class AI(GenericAI):
    """Agent using Strength Difference Checking (SDC) strategy

    This agent prefers moves with highest strength difference 
    and doesn't make moves against areas with higher strength.
    """
    def __init__(self, game):
        """
        Parameters
        ----------
        game : Game

        Attributes
        ----------
        possible_attackers : list of int
            Areas that can make an attack
        attacks_done : list of int
        """
        super(AI, self).__init__(game)
        self.possible_attackers = []
        self.attacks_done = []

    def ai_turn(self):
        """AI agent's turn

        Creates a list with all possible moves along with associated strength 
        difference. The list is then sorted in descending order with respect to 
        the SD. A move with the highest SD is then made unless the highest 
        SD is lower than zero - in this case, the agent ends its turn.
        """

        areas = list(self.board.areas.values())
        shuffle(areas)
        attacks = []

        for area in areas:
            area_dice = area.get_dice()
            if area_dice is 1:
                continue
            if area.get_owner_name() == self.player_name:
                neighbours = area.get_adjacent_areas()
                shuffle(neighbours)

                for adj in neighbours:
                    adjacent_area = self.board.get_area(adj)
                    if adjacent_area.get_owner_name() != self.player_name:
                        strength_difference = area_dice - adjacent_area.get_dice()
                        attack = [area.get_name(), adj, strength_difference]
                        attacks.append(attack)

        attacks = sorted(attacks, key=lambda attack: attack[2], reverse=True)

        if attacks and attacks[0][2] >= 0:
            self.send_message('battle', attacks[0][0], attacks[0][1])
            self.waitingForResponse = True
            return True

        self.send_message('end_turn')
        self.waitingForResponse = True

        return True
