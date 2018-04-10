from random import shuffle

from ai import GenericAI


class AI(GenericAI):
    """Strength difference checking.

    This AI prefers moves with the highest possible difference of strength when
    chosing territories to attack. It passes when no moves are found with strength
    difference of at least 0.
    """
    def __init__(self, game, verbose):
        super(AI, self).__init__(game, verbose)
        self.ai_version = 2

    def ai_turn(self):
        areas = list(self.board.areas.values())
        shuffle(areas)

        for i in range(7, -1, -1):
            for area in areas:
                if area.get_owner_name() == self.player_name:
                    area_dice = area.get_dice()
                    neighbours = area.get_adjacent_areas(self.board)
                    shuffle(neighbours)

                    for adj in neighbours:
                        adjacent_area = self.board.get_area(adj)
                        if adjacent_area.get_owner_name() != self.player_name:
                            if area_dice > 1 and area_dice - adjacent_area.get_dice() >= i:
                                self.send_message('battle', attacker=area.get_name(), defender=adjacent_area.get_name())
                                self.waitingForResponse = True
                                return True

        self.send_message('end_turn')
        self.waitingForResponse = True

        return True
