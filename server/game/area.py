import logging


class Area(object):
    def __init__(self, name, adjacent_areas):
        self.name = name
        self.adjacent_areas_names = adjacent_areas
        self.logger = logging.getLogger('SERVER')

        self.adjacent_areas = []
        self.dice = 0
        self.owner_name = None

    def add_adjacent_areas(self, board):
        for name in self.adjacent_areas_names:
            self.adjacent_areas.append(board.areas[name])

    def add_die(self):
        if self.dice >= 8:
            self.dice = 8
            return False
        else:
            self.dice += 1
            return True

    def get_adjacent_areas(self):
        return self.adjacent_areas

    def get_adjacent_areas_names(self):
        return self.adjacent_areas_names

    def get_dice(self):
        return self.dice

    def get_name(self):
        return self.name

    def get_owner_name(self):
        if not self.owner_name:
            return False
        else:
            return self.owner_name

    def set_dice(self, dice):
        if dice < 1 or dice > 8:
            self.logger.warning("Trying to assign {0} dice to area {1}"\
                                .format(dice, self.name))
        else:
            self.dice = dice

    def set_owner_name(self, name):
        self.owner_name = name

    def set_to_one_die(self):
        self.dice = 1
