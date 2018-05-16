from random import shuffle
from pprint import pprint

from ai import GenericAI
from ai.utils import attack_succcess_probability, probability_of_holding_area, probability_of_successful_attack


class AI(GenericAI):
    """Agent using improved Signle Turn Expectiminimax (STEi) strategy

    This agent makes such moves that have a probability of successful
    attack and hold over the area until next turn higher a 20% in two-player
    gams and higher than 40% in four-player games. In addition, it prefers 
    attacks initiated from its largest region.
    """
    def __init__(self, game):
        """
        Parameters
        ----------
        game : Game
        
        Attributes
        ----------
        treshold : float
            Probability treshold for choosing an attack
        score_weight: float
            Preference of an attack from largest region over other attacks
        """
        super(AI, self).__init__(game)
        self.new_turn = False
        self.players = len(self.game.players)
        if self.players == 2:
            self.treshold = 0.2
            self.score_weight = 3
        else:
            self.treshold = 0.4
            self.score_weight = 2
        self.attacked = False

        self.possible_attackers = []
        self.largest_region  = []

    def ai_turn(self):
        """AI agent's turn

        Agent gets a list preferred moves and makes such move that has the 
        highest estimated hold probability, prefering moves initiated from within 
        the largest region. If there is no such move, the agent ends it's turn.
        """
        self.logger.debug("Looking for possible turns.")
        self.get_largest_region()
        turns = self.possible_turns()

        if turns:
            turn = turns[0]
            area_name = turn[0]
            self.logger.debug("Possible turn: {}".format(turn))
            atk_area = self.board.get_area(turn[0])
            atk_power = atk_area.get_dice()
            hold_prob = turn[3]
            self.logger.debug("{0}->{1} attack and hold probabiliy {2}".format(turn[0], turn[1], hold_prob))

            self.send_message('battle', attacker=turn[0], defender=turn[1])
            self.waitingForResponse = True
            return True

        self.logger.debug("No more plays.")

        self.send_message('end_turn')
        self.waitingForResponse = True

        return True

    def possible_turns(self):
        """Find possible turns with hold higher hold probability than treshold

        This method returns list of all moves with probability of holding the area
        higher than the treshold or areas with 8 dice. In addition, it includes 
        the preference of these moves. The list is sorted in descending order with
        respect to preference * hold probability
        """
        turns = []
        for area in self.board.areas.values():
            if area.get_owner_name() == self.player_name and area.get_dice() > 1:
                for adj in area.get_adjacent_areas():
                    adjacent_area = self.board.get_area(adj)
                    if adjacent_area.get_owner_name() != self.player_name:
                        area_name = area.get_name()
                        if area_name not in self.possible_attackers:
                            self.possible_attackers.append(area_name)

                        atk_power = area.get_dice()
                        atk_prob = probability_of_successful_attack(self.board, area_name, adj)
                        hold_prob = atk_prob * probability_of_holding_area(self.board, adj, atk_power - 1, self.player_name)
                        if hold_prob >= self.treshold or atk_power is 8:
                            preference = hold_prob
                            if area_name in self.largest_region:
                                preference *= self.score_weight
                            turns.append([area.get_name(), adj, preference, hold_prob])

        return sorted(turns, key=lambda turn: turn[2], reverse=True)

    def get_largest_region(self):
        """Get size of the largest region, including the areas within

        Attributes
        ----------
        largest_region : list of int
            Names of areas in the largest region

        Returns
        -------
        int
            Number of areas in the largest region
        """
        board = self.game.board
        self.largest_region = []
        largest_region_size = 0
        largest_region = [] # names of areas in largest region
        areas_to_test = []
        player_areas = []

        for area in self.board.areas.values():
            if area.get_owner_name() == self.player_name:
                areas_to_test.append(area.get_name())

        if not areas_to_test:
            return 0

        areas_in_current_region = [areas_to_test[0]]

        while areas_to_test:
            areas_already_tested = []
            while areas_in_current_region:
                current_area = areas_in_current_region[0]
                areas_in_current_region.remove(current_area)
                areas_already_tested.append(current_area)

                for area in board.get_area(current_area).get_adjacent_areas():
                    if (area not in areas_already_tested and
                        area not in areas_in_current_region):
                        if board.get_area(area).get_owner_name() == self.player_name:
                            areas_in_current_region.append(area)

            if len(areas_already_tested) > largest_region_size:
                for area in areas_already_tested:
                    largest_region.append(area)
                largest_region_size = len(areas_already_tested)

            for area in areas_already_tested:
                if area in areas_to_test:
                    areas_to_test.remove(area)
                    player_areas.append(area)

            if areas_to_test:
                areas_in_current_region = [areas_to_test[0]]

        for area in largest_region:
            self.largest_region.append(area)
        return largest_region_size
