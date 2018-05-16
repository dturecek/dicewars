import numpy

from random import shuffle

from ai import GenericAI
from ai.utils import attack_succcess_probability , probability_of_successful_attack, sigmoid


class AI(GenericAI):
    """Agent using Win Probability Maximization (WPM) using player scores

    This agent estimates win probability given the current state of the game.
    As a feature to describe the state, a vector of players' scores is used.
    The agent choses such moves, that will have the highest improvement in
    the estimated probability.
    """
    def __init__(self, game):
        """
        Parameters
        ----------
        game : Game

        Attributes
        ----------
        players_order : list of int
            Names of players in the order they are playing, with the agent being first
        weights : dict of numpy.array
            Weights for estimating win probability
        largest_region: list of int
            Names of areas in the largest region
        """
        super(AI, self).__init__(game)
        self.players = len(self.game.players)

        self.largest_region  = []

        self.players_order = game.players_order
        while self.player_name != self.players_order[0]:
            self.players_order.append(self.players_order.pop(0))

        self.weights = {
            2: numpy.array([0.51862355, -0.417179]),
            3: numpy.array([0.24112347, -0.20702862, -0.20097175]),
            4: numpy.array([0.26457488, -0.20733951, -0.19326027, -0.20171941]),
            5: numpy.array([0.26777938, -0.1878346, -0.18560973, -0.20005864, -0.18976791]),
            6: numpy.array([0.2700982, -0.18000744, -0.18290534, -0.1815374, -0.20105069, -0.1808327]),
            7: numpy.array([0.27109102, -0.18051686, -0.18232428, -0.17905882, -0.17959111, -0.17958394, -0.17634735]),
            8: numpy.array([0.277179, -0.16852433, -0.18678373, -0.17492631, -0.17996621, -0.1790844, -0.16977776, -0.18876063]),
        }[self.players]

    def ai_turn(self):
        """AI agent's turn

        This agent estimates probability to win the game from the feature vector associated
        with the outcome of the move and chooses such that has highest improvement in the
        probability.
        """
        self.logger.debug("Looking for possible turns.")
        turns = self.possible_turns()

        if turns:
            turn = turns[0]
            area_name = turn[0]
            self.logger.debug("Possible turn: {}".format(turn))
            atk_area = self.board.get_area(turn[0])
            atk_power = atk_area.get_dice()

            if turn[2] >= -0.05 or atk_power == 8:
                self.send_message('battle', attacker=turn[0], defender=turn[1])
                self.waitingForResponse = True
                return True

        self.logger.debug("No more plays.")
        self.send_message('end_turn')
        self.waitingForResponse = True

        return True

    def possible_turns(self):
        """Get list of possible turns with the associated improvement
        in estimated win probability
        """
        turns = []

        features = []
        for p in self.players_order:
            features.append(self.get_score_by_player(p))
        win_prob = numpy.log(sigmoid(numpy.dot(numpy.array(features), self.weights)))

        self.get_largest_region()

        for area in self.board.areas.values():
            # area belongs to the player and has strength to attack
            if area.get_owner_name() == self.player_name and area.get_dice() > 1:
                area_name = area.get_name()
                atk_power = area.get_dice()

                for adj in area.get_adjacent_areas():
                    adjacent_area = self.board.get_area(adj)

                    # adjacent area belongs to an opponent
                    opponent_name = adjacent_area.get_owner_name()
                    if opponent_name != self.player_name:
                        # check whether the attack would expand the largest region
                        increase_score = False
                        if area_name in self.largest_region:
                            increase_score = True
                        else:
                            for n in adjacent_area.get_adjacent_areas():
                                if n in self.largest_region:
                                    increase_score = True
                                    break

                        if increase_score or atk_power is 8:
                            atk_prob = numpy.log(probability_of_successful_attack(self.board, area_name, adj))
                            new_features = []
                            for p in self.players_order:
                                idx = self.players_order.index(p)
                                if p == self.player_name:
                                    new_features.append(features[idx] + 1 if increase_score else features[idx])
                                elif p == opponent_name:
                                    new_features.append(self.get_score_by_player(p, skip_area=adj))
                                else:
                                    new_features.append(features[idx])
                            new_win_prob = numpy.log(sigmoid(numpy.dot(numpy.array(new_features), self.weights)))
                            total_prob = new_win_prob + atk_prob
                            improvement = total_prob - win_prob
                            if improvement >= -1:
                                turns.append([area_name, adj, improvement])

        return sorted(turns, key=lambda turn: turn[2], reverse=True)

    def get_score_by_player(self, player_name, skip_area=None):
        """Get score of a player

        Parameters
        ----------
        player_name : int
        skip_area : int
            Name of an area to be excluded from the calculation

        Returns
        -------
        int
            score of the player
        """
        board = self.game.board
        score = 0
        areas_to_test = []
        player_areas = []

        # Find player areas and skip the area specified by skip_area
        for area in self.board.areas.values():
            if (area.get_owner_name() == player_name and area.get_name() != skip_area):
                areas_to_test.append(area.get_name())

        if not areas_to_test:
            return 0

        areas_in_current_region = [areas_to_test[0]]
        # Iterate over all areas belonging to the player
        while areas_to_test:
            areas_already_tested = []
            # Iterate over a single region
            while areas_in_current_region:
                current_area = areas_in_current_region[0]
                areas_in_current_region.remove(current_area)
                areas_already_tested.append(current_area)

                for area in board.get_area(current_area).get_adjacent_areas():
                    if (area not in areas_already_tested and
                        area not in areas_in_current_region and
                        area != skip_area):
                        if board.get_area(area).get_owner_name() == player_name:
                            areas_in_current_region.append(area)

            if len(areas_already_tested) > score:
                score = len(areas_already_tested)

            # Remove areas in the current region from the areas yet to be tested
            for area in areas_already_tested:
                if area in areas_to_test:
                    areas_to_test.remove(area)
                    player_areas.append(area)

            if areas_to_test:
                areas_in_current_region = [areas_to_test[0]]

        return score

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
        largest_regions = [] # names of areas in largest regions
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

            region_size = len(areas_already_tested)
            if region_size >= largest_region_size:
                region = []
                for area in areas_already_tested:
                    region.append(area)
                if region_size > largest_region_size:
                    largest_regions = []
                largest_regions.append(region)
                largest_region_size = region_size

            for area in areas_already_tested:
                if area in areas_to_test:
                    areas_to_test.remove(area)
                    player_areas.append(area)

            if areas_to_test:
                areas_in_current_region = [areas_to_test[0]]

        for region in largest_regions:
            for area in region:
                self.largest_region.append(area)
        return largest_region_size
