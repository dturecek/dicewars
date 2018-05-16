import logging
import socket


class Player(object):
    """Object representing a player
    """
    def __init__(self, name):
        """
        Parameters
        ----------
        name : int
            Player's name

        Attributes
        ----------
        areas : list of Area
            Areas belonging to the player
        dice_reserve : int
            Number of dice in player's reserve
        client_addr : str
            Client's IP address
        client_port : int
            Client's port number
        socket : socket
            Client's socket
        """

        self.name = name
        self.logger = logging.getLogger('SERVER')

        self.areas = []
        self.client_addr = None
        self.client_port = None
        self.socket = None
        self.dice_reserve = 0

    def add_area(self, area):
        """Add area to player's areas
        """
        if area in self.areas:
            self.logger.warning("Area {0} already belonging to player {1}."\
                                .format(area.get_name(), self.name))
        else:
            self.areas.append(area)

    def assign_client(self, socket, client_addr):
        """Assign client's socket, IP address, and port number
        
        Parameters
        ----------
        socket : socket
        client_addr : (str, int)
            IP address and port number
        """
        self.socket = socket
        self.client_addr = client_addr[0]
        self.client_port = client_addr[1]
        self.logger.info("Assigning socket {0} with IP {1}:{2} to player {3}"\
                         .format(socket, client_addr[0], client_addr[1],
                                 self.name))

    def get_areas(self):
        """Get areas controlled by the player

        Returns
        -------
        list of Area
        """
        return self.areas

    #def get_areas_names(self):
    #    return ','.join(str(a.get_name()) for a in self.areas)

    def get_largest_region(self, board):
        """Get player's score

        Parameters
        ----------
        board : Board

        Returns
        -------
        int
            Player's score
        """
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

        self.areas = player_areas
        return largest_region_size

    def get_name(self):
        """Return player's name
        """
        return self.name

    def get_number_of_areas(self):
        """Return number of areas under Player's control
        """
        return len(self.areas)

    def get_reserve(self):
        """Return number of dice in Player's reserve
        """
        return self.dice_reserve

    def has_client(self):
        if self.socket: return True
        else: return False

    def remove_area(self, area):
        """Remove area from list of areas controlled by the player
        """
        if area not in self.areas:
            self.logger.warning("Trying to remove area {0} that doesn't\
                                belong to player {1}".format(area.get_name(),
                                self.name))
        else:
            self.areas.remove(area)

    def send_message(self, msg):
        """Send message msg to the Player's client
        """
        try:
            self.socket.sendall(msg.encode())
        except socket.error as e:
            self.logger.error("Connection to client {0} broken".format(
                              self.name))
            raise e

    def set_reserve(self, dice):
        """Set dice reserve
        """
        self.dice_reserve = dice

    def total_areas(self):
        """Return number of areas under Player's control
        """
        return len(self.areas)
        
    def total_dice(self):
        """Return total number of Player's dice
        """
        td = 0
        for area in self.areas:
            td += area.get_dice()
        return td

