from random import shuffle

from ai import GenericAI
from ai.utils import attack_succcess_probability, probability_of_holding_area, probability_of_successful_attack


class AI(GenericAI):
    """Single turn expectiminimax v0.

    This AI checks the probability of attack and then the probability to hold
    a territory through next player's turn.
    """
    def __init__(self, game, verbose):
        super(AI, self).__init__(game, verbose)
        self.ai_version = 3

    def ai_turn(self):
        self.logger.debug("Looking for possible turns.")
        turns = self.possible_turns()
        prob = 0.7
        while True:
            for turn in turns:
                self.logger.debug("Possible turn: {}".format(turn))
                atk_area = self.board.get_area(turn[0])
                atk_power = atk_area.get_dice()
                atk_prob = probability_of_successful_attack(self.board, turn[0], turn[1])
                self.logger.debug("{0}->{1} attack probabiliy {2}".format(turn[0], turn[1], atk_prob))
                if atk_prob > prob:
                    hold_prob = probability_of_holding_area(self.board, turn[1], atk_power - 1, self.player_name)
                    self.logger.debug("{0} hold probability {1}".format(turn[1], hold_prob))
                    if hold_prob > prob:
                        self.send_message('battle', attacker=turn[0], defender=turn[1])
                        self.waitingForResponse = True
                        return True

            prob -= 0.1
            if prob < 0.2:
                for turn in turns:
                    atk_area = self.board.get_area(turn[0])
                    atk_power = atk_area.get_dice()
                    if atk_power is not 8:
                        continue

                    atk_prob = probability_of_successful_attack(self.board, turn[0], turn[1])
                    hold_prob = probability_of_holding_area(self.board, turn[1], atk_power - 1, self.player_name)

                    self.send_message('battle', attacker=turn[0], defender=turn[1])
                    self.waitingForResponse = True
                    return True
                break

        self.logger.debug("No more plays.")
        self.send_message('end_turn')
        self.waitingForResponse = True

        return True

    def possible_turns(self):
        turns = []
        for area in self.board.areas.values():
            if area.get_owner_name() == self.player_name and area.get_dice() > 1:
                for adj in area.get_adjacent_areas(self.board):
                    adjacent_area = self.board.get_area(adj)
                    if adjacent_area.get_owner_name() != self.player_name:
                        turns.append([area.get_name(), adj])
        shuffle(turns)
        return turns
