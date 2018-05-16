from random import shuffle

from ai import GenericAI
from ai.utils import attack_succcess_probability, probability_of_holding_area, probability_of_successful_attack


class AI(GenericAI):
    """Agent using Single Turn Expectiminimax (STE) strategy

    This agent makes such moves that have a probability of successful
    attack and hold over the area until next turn higher than 20 %.
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

        Agent gets a list preferred moves and makes such move that has the 
        highest estimated hold probability. If there is no such move, the agent
        ends it's turn.
        """
        self.logger.debug("Looking for possible turns.")
        turns = self.possible_turns()

        if turns:
            turn = turns[0]
            area_name = turn[0]
            self.logger.debug("Possible turn: {}".format(turn))
            atk_area = self.board.get_area(area_name)
            atk_power = atk_area.get_dice()
            hold_prob = turn[2]
            self.logger.debug("{0}->{1} attack and hold probabiliy {2}".format(area_name, turn[1], hold_prob))

            self.send_message('battle', attacker=area_name, defender=turn[1])
            self.waitingForResponse = True
            return True


        self.logger.debug("No more plays.")
        self.send_message('end_turn')
        self.waitingForResponse = True

        return True

    def possible_turns(self):
        """Get a list of preferred moves

        This list is sorted with respect to hold probability in descending order.
        It includes all moves that either have hold probability higher or equal to 20 %
        or have strength of eight dice.
        """
        turns = []
        for area in self.board.areas.values():
            if area.get_owner_name() == self.player_name and area.get_dice() > 1:
                for adj in area.get_adjacent_areas():
                    adjacent_area = self.board.get_area(adj)
                    if adjacent_area.get_owner_name() != self.player_name:
                        area_name = area.get_name()
                        atk_power = area.get_dice()
                        atk_prob = probability_of_successful_attack(self.board, area_name, adj)
                        hold_prob = atk_prob * probability_of_holding_area(self.board, adj, atk_power - 1, self.player_name)
                        if hold_prob >= 0.2 or atk_power is 8:
                            turns.append([area_name, adj, hold_prob])

        return sorted(turns, key=lambda turn: turn[2], reverse=True)
