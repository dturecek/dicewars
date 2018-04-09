from random import shuffle

from ai import GenericAI
from ai.utils import attack_succcess_probability

class AI(GenericAI):
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
                atk_prob = self.probability_of_successful_attack(turn[0], turn[1])
                self.logger.debug("{0}->{1} attack probabiliy {2}".format(turn[0], turn[1], atk_prob))
                if atk_prob > prob:
                    hold_prob = self.probability_of_holding_area(turn[1], atk_power - 1)
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

                    atk_prob = self.probability_of_successful_attack(turn[0], turn[1])
                    hold_prob = self.probability_of_holding_area(turn[1], atk_power - 1)

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

    def probability_of_holding_area(self, area_name, area_dice):
        area = self.board.get_area(area_name)
        probability = 1.0
        for adj in area.get_adjacent_areas(self.board):
            adjacent_area = self.board.get_area(adj)
            if adjacent_area.get_owner_name() != self.player_name:
                enemy_dice = adjacent_area.get_dice()
                if enemy_dice is 1:
                    continue
                lose_prob = attack_succcess_probability(enemy_dice, area_dice)
                hold_prob = 1.0 - lose_prob
                probability *= hold_prob
        return probability

    def probability_of_successful_attack(self, atk_area, target_area):
        atk = self.board.get_area(atk_area)
        target = self.board.get_area(target_area)
        atk_power = atk.get_dice()
        def_power = target.get_dice()
        return attack_succcess_probability(atk_power, def_power)
