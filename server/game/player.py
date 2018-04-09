import logging
import socket


class Player(object):
    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger('SERVER')

        self.areas = []
        self.areas_not_full = []
        self.client_addr = None
        self.client_port = None
        self.socket = None
        self.dice_reserve = 0

    def add_area(self, area):
        if area in self.areas:
            self.logger.warning("Area {0} already belonging to player {1}."\
                                .format(area.get_name(), self.name))
        else:
            self.areas.append(area)
            if area.get_dice() < 8:
                self.areas_not_full.append(area)

    def assign_client(self, socket, client_addr):
        self.socket = socket
        self.client_addr = client_addr[0]
        self.client_port = client_addr[1]
        self.logger.info("Assigning socket {0} with IP {1}:{2} to player {3}"\
                         .format(socket, client_addr[0], client_addr[1],
                                 self.name))

    def get_areas(self):
        return self.areas

    def get_areas_names(self):
        return ','.join(str(a.get_name()) for a in self.areas)

    def get_largest_region(self, board):
        largest_region_size = 0
        areas_to_test = self.areas
        player_areas = []

        if not areas_to_test:
            return 0

        areas_in_current_region = [areas_to_test[0]]

        while areas_to_test:
            areas_already_tested = []
            while areas_in_current_region:
                current_area = areas_in_current_region[0]
                areas_in_current_region.remove(current_area)
                areas_already_tested.append(current_area)

                for area in current_area.get_adjacent_areas():
                    if (area not in areas_already_tested and
                        area not in areas_in_current_region):
                        if area.get_owner_name() == self.name:
                            areas_in_current_region.append(area)

            if len(areas_already_tested) > largest_region_size:
                largest_region_size = len(areas_already_tested)

            for area in areas_already_tested:
                if area in areas_to_test:
                    areas_to_test.remove(area)
                    player_areas.append(area)

            if areas_to_test:
                areas_in_current_region = [areas_to_test[0]]

        self.areas = player_areas #TODO is this needed?
        return largest_region_size

    def get_name(self):
        return self.name

    def get_number_of_areas(self):
        return len(self.areas)

    def get_reserve(self):
        return self.dice_reserve

    def has_client(self):
        if self.socket: return True
        else: return False

    def print_areas(self):
        self.logger.debug("Player {0} areas: {1}".format(self.name,
            ','.join(str(a.get_name) for a in self.areas)))

    def remove_area(self, area):
        if area not in self.areas:
            self.logger.warning("Trying to remove area {0} that doesn't\
                                belong to player {1}".format(area.get_name(),
                                self.name))
        else:
            self.areas.remove(area)
        if area in self.areas_not_full:
            self.areas_not_full.remove(area)

    def send_message(self, msg):
        try:
            self.socket.sendall(msg.encode())
        except socket.error as e:
            self.logger.error("Connection to client {0} broken".format(
                              self.name))
            raise e

    def set_reserve(self, dice):
        self.dice_reserve = dice
