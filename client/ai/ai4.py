from random import shuffle

from ai import GenericAI
from ai.utils import attack_succcess_probability, probability_of_holding_area, probability_of_successful_attack


class AI(GenericAI):
    """Single turn expectiminimax.

    When chosing a move, this AI prefers such that has the highest probability
    to conquer and hold a territory through next player's turn.

    If no move with this probability higher than 20% can be made, it attacks
    from a territory with strength of 8, if possible.
    """
    def __init__(self, game, verbose):
        super(AI, self).__init__(game, verbose)
        self.ai_version = 4

    def ai_turn(self):
        self.logger.debug("Looking for possible turns.")
        turns = self.possible_turns()

        if turns:
            turn = turns[0]
            self.logger.debug("Possible turn: {}".format(turn))
            atk_area = self.board.get_area(turn[0])
            atk_power = atk_area.get_dice()
            hold_prob = turn[2]
            self.logger.debug("{0}->{1} attack and hold probabiliy {2}".format(turn[0], turn[1], hold_prob))
            self.send_message('battle', attacker=turn[0], defender=turn[1])
            self.waitingForResponse = True
            return True

        self.logger.debug("No more plays.")
        self.send_message('end_turn')
        self.new_turn = True
        self.waitingForResponse = True

        return True

    def possible_turns(self):
        turns = []
        for area in self.board.areas.values():
            if area.get_owner_name() == self.player_name and area.get_dice() > 1:
                for adj in area.get_adjacent_areas():
                    adjacent_area = self.board.get_area(adj)
                    if adjacent_area.get_owner_name() != self.player_name:
                        atk_power = area.get_dice()
                        atk_prob = probability_of_successful_attack(self.board, area.get_name(), adj)
                        hold_prob = atk_prob * probability_of_holding_area(self.board,
                                                    adj, atk_power - 1,
                                                    self.player_name)
                        if hold_prob >= 0.2 or atk_power is 8:
                            turns.append([area.get_name(), adj, hold_prob])

        return sorted(turns, key=lambda turn: turn[2], reverse=True)
