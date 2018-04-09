from random import shuffle

from ai import GenericAI

class AI(GenericAI):
    def __init__(self, game, verbose):
        super(AI, self).__init__(game, verbose)
        self.ai_version = 1

    def ai_turn(self):
        areas = list(self.board.areas.values())
        shuffle(areas)
        for area in areas:
            if area.get_owner_name() == self.player_name and area.get_dice() > 1:
                neighbours = area.get_adjacent_areas(self.board)
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
