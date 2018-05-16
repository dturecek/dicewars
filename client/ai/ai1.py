from random import shuffle

from ai import GenericAI


class AI(GenericAI):
    """Naive player agent
    
    This agent performs all possible moves in random order
    """

    def __init__(self, game):
        """
        Parameters
        ----------
        game : Game
        """
        super(AI, self).__init__(game)

    def ai_turn(self):
        """AI agent's turn

        Get a random area. If it has a possible move, the agent will do it. 
        If there are no more moves, the agent ends its turn.
        """
        areas = list(self.board.areas.values())
        shuffle(areas)
        for area in areas:
            if area.get_owner_name() == self.player_name and area.get_dice() > 1:
                neighbours = area.get_adjacent_areas()
                shuffle(neighbours)
                for adj in neighbours:
                    adjacent_area = self.board.get_area(adj)
                    if adjacent_area.get_owner_name() != self.player_name:
                        self.send_message('battle', attacker=area.get_name(), defender=adjacent_area.get_name())
                        self.waitingForResponse = True
                        return True

        self.logger.debug("No more possible turns.")
        self.send_message('end_turn')
        self.waitingForResponse = True

        return True
