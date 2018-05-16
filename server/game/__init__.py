import json
from json.decoder import JSONDecodeError
import logging
import os
import random
import socket

from game.board import Board
from game.generator import BoardGenerator
from game.player import Player


class Game(object):
    """Instance of the game
    """
    def __init__(self, players, addr, port):
        """Initialize game and connect clients

        Parameters
        ----------
        players : int
            Number of players
        addr : str
            IP address of the server
        port : int
            Port number

        Attributes
        ----------
        buffer : int
            Size of socket buffer
        number_of_players : int
            Number of players
        """
        self.buffer = 65535
        self.logger = logging.getLogger('SERVER')

        self.address = addr
        self.port = port
        self.number_of_players = players

        self.create_socket()
        self.initialize_game()
        self.connect_clients()


    def run(self):
        """Main loop of the game
        """
        try:
            for i in range(1, self.number_of_players + 1):
                player = self.players[i]
                self.send_message(player, 'game_state')
            while True:
                self.logger.debug("Current player {}".format(self.current_player.get_name()))
                self.handle_player_turn()
                if self.check_win_condition():
                    break

        except KeyboardInterrupt:
            self.logger.info("Game interrupted.")
            for i in range(1, self.number_of_players + 1):
                player = self.players[i]
                self.send_message(player, 'close_socket')
        except (BrokenPipeError, JSONDecodeError) as e:
            self.logger.error("Connection to client failed: {0}".format(e))
        except ConnectionResetError:
            self.logger.error("ConnectionResetError")

        try:
            self.close_connections()
        except BrokenPipeError:
            pass

    ##############
    # GAME LOGIC #
    ##############
    def assign_area(self, area, player):
        """Assign area to a new owner

        Parameters
        ----------
        area : Area
            Area to be assigned new owner to
        player : Player
            New owner
        """
        area.set_owner_name(player.get_name())
        player.add_area(area)

    def handle_player_turn(self):
        """Handle clients message and carry out the action
        """
        self.logger.debug("Handling player {} turn".format(self.current_player.get_name()))
        player = self.current_player.get_name()
        msg = self.get_message(player)

        if msg['type'] == 'battle':
            atk_dice = self.board.get_area_by_name(msg['atk']).get_dice()
            def_name = self.board.get_area_by_name(msg['def']).get_owner_name()
            battle = self.battle(self.board.get_area_by_name(msg['atk']), self.board.get_area_by_name(msg['def']))
            self.logger.debug("Battle result: {}".format(battle))
            for p in self.players:
                self.send_message(self.players[p], 'battle', battle=battle)

        elif msg['type'] == 'end_turn':
            affected_areas = self.end_turn()
            for p in self.players:
                self.send_message(self.players[p], 'end_turn', areas=affected_areas)

    def get_state(self):
        """Get game state

        Returns
        -------
        dict
            Dictionary containing owner, dice and adjacent areas of 
            each area, as well as score of each player
        """
        game_state = {
            'areas': {}
        }

        for a in self.board.areas:
            area = self.board.areas[a]
            game_state['areas'][area.name] = {
                'adjacent_areas': area.get_adjacent_areas_names(),
                'owner': area.get_owner_name(),
                'dice': area.get_dice()
            }

        game_state['score'] = {}

        for p in self.players:
            player = self.players[p]
            game_state['score'][player.get_name()] = player.get_largest_region(self.board)

        return game_state

    def battle(self, attacker, defender):
        """Carry out a battle

        Returns
        -------
        dict
            Dictionary with the result of the battle including information
            about rolled numbers, dice left after the battle, and possible 
            new ownership of the areas
        """
        atk_dice = attacker.get_dice()
        def_dice = defender.get_dice()
        atk_pwr = def_pwr = 0

        atk_name = attacker.get_owner_name()
        def_name = defender.get_owner_name()

        for i in range(0, atk_dice):
            atk_pwr += random.randint(1,6)
        for i in range(0, def_dice):
            def_pwr += random.randint(1,6)

        battle = {
            'atk': {
                'name': attacker.get_name(),
                'dice': 1,
                'owner': atk_name,
                'pwr': atk_pwr
            }
        }

        attacker.set_dice(1)

        if atk_pwr > def_pwr:
            defender.set_owner_name(atk_name)
            self.players[atk_name].add_area(defender)
            self.players[def_name].remove_area(defender)
            attacker.set_dice(1)
            defender.set_dice(atk_dice - 1)
            battle['def'] = {
                'name': defender.get_name(),
                'dice': atk_dice - 1,
                'owner': atk_name,
                'pwr': def_pwr
            }

        else:
            battle['def'] = {
                'name': defender.get_name(),
                'dice': def_dice,
                'owner': def_name,
                'pwr': def_pwr
            }

        return battle

    def end_turn(self):
        """Handles end turn command
        
        Returns
        -------
        dict
            Dictionary of affected areas including number of dice in these areas
        """
        affected_areas = []
        player = self.current_player
        dice = player.get_reserve() + player.get_largest_region(self.board)
        if dice > 64:
            dice = 64

        areas = []
        for area in self.current_player.get_areas():
            areas.append(area)

        while dice and areas:
            area = random.choice(areas)
            if not area.add_die():
                areas.remove(area)
            else:
                if area not in affected_areas:
                    affected_areas.append(area)
                dice -= 1

        player.set_reserve(dice)

        self.set_next_player()

        list_of_areas = {}
        for area in affected_areas:
            list_of_areas[area.get_name()] = {
                'owner': area.get_owner_name(),
                'dice': area.get_dice()
            }

        return list_of_areas

    def set_first_player(self):
        """Set first player
        """
        for player in self.players:
            if self.players[player].get_name() == self.players_order[0]:
                self.current_player = self.players[player]
                self.logger.debug("Current player: {}".format(self.current_player.get_name()))
                return

    def set_next_player(self):
        """Set next player in order as a current player
        """
        current_player_name = self.current_player.get_name()
        current_idx = self.players_order.index(current_player_name)
        idx = self.players_order[(current_idx + 1) % self.number_of_players]
        while True:
            try:
                if self.players[idx].get_largest_region(self.board) == 0:
                    current_idx = (current_idx + 1) % self.number_of_players
                    idx = self.players_order[(current_idx + 1) % self.number_of_players]
                    continue
                self.current_player = self.players[idx]
                self.logger.debug("Current player: {}".format(self.current_player.get_name()))
            except IndexError:
                exit(1)
            return

    def check_win_condition(self):
        """Check win conditions

        Returns
        -------
        bool
            True if a player has won, False otherwise
        """
        for p in self.players:
            player = self.players[p]
            if player.get_number_of_areas() == self.board.get_number_of_areas():
                self.logger.info("Player {} wins!".format(player.get_name()))
                for i in self.players:
                    self.send_message(self.players[i], 'game_end', winner=player.get_name())
                return True

        return False

    ##############
    # NETWORKING #
    ##############
    def get_message(self, player):
        """Read message from client

        Parameters
        ----------
        player : int
            Name of the client

        Returns
        -------
        str
            Decoded message from the client
        """
        raw_message = self.client_sockets[player].recv(self.buffer)
        msg = json.loads(raw_message.decode())
        self.logger.debug("Got message from client {}; type: {}".format(player, msg['type']))
        return msg

    def send_message(self, client, type, battle=None, winner=None, areas=None):
        """Send message to a client

        Parameters
        ----------
        client : Player
            Recepient of the message
        type : str
            Type of message
        battle : dict
            Result of a battle
        winner : int
            Winner of the game
        areas : list of int
            Areas changed during the turn
        """
        self.logger.debug("Sending msg type '{}' to client {}".format(type, client.get_name()))
        if type == 'game_start':
            msg = self.get_state()
            msg['type'] = 'game_start'
            msg['player'] = client.get_name()
            msg['no_players'] = self.number_of_players
            msg['current_player'] = self.current_player.get_name()
            msg['board'] = self.board.get_board()
            msg['order'] = self.players_order

        elif type == 'game_state':
            msg = self.get_state()
            msg['type'] = 'game_state'
            msg['player'] = client.get_name()
            msg['no_players'] = self.number_of_players
            msg['current_player'] = self.current_player.get_name()

        elif type is 'battle':
            msg = self.get_state()
            msg['type'] = 'battle'
            msg['result'] = battle

        elif type is 'end_turn':
            msg = self.get_state()
            msg['type'] = 'end_turn'
            msg['areas'] = areas
            msg['current_player'] = self.current_player.get_name()
            msg['reserves'] = {
                i: self.players[i].get_reserve() for i in self.players
            }

        elif type is 'game_end':
            msg = {
                'type': 'game_end',
                'winner': winner
            }

        elif type == 'close_socket':
            msg = {'type': 'close_socket'}

        msg = json.dumps(msg)
        client.send_message(msg + '\0')

    def create_socket(self):
        """Initiate server socket
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.address, self.port))
            self.logger.debug("Server socket at {}:{}".format(self.address, self.port))
        except OSError as e:
            self.logger.error("Cannot create socket. {0}.".format(e))
            exit(1)

    def connect_clients(self):
        """Connect all clients
        """
        self.client_sockets = {}

        self.socket.listen(self.number_of_players)
        self.logger.debug("Waiting for clients to connect")

        for i in range(1, self.number_of_players + 1):
            self.connect_client(i)
        self.logger.debug("Successfully assigned clients to all players")

    def connect_client(self, i):
        """Assign client to an instance of Player
        """
        sock, client_address = self.socket.accept()
        player = self.add_client(sock, client_address, i)
        self.send_message(player, 'game_start')

    def add_client(self, connection, client_address, i):
        """Add client's socket to an instance of Player

        Parameters
        ----------
        connection : socket
            Client's socket
        client_addres : (str, int)
            Client's address and port number
        i : int
            Player's name
        
        Returns
        -------
        Player
            Instance of Player that the client was assigned to
        """
        self.client_sockets[i] = connection
        player = self.assign_player_to_client(connection, client_address)
        if not player:
            raise Exception("Could not assign player to client {}".format(client_address))
        else:
            return player

    def assign_player_to_client(self, socket, client_address):
        """Add client's socket to an unassigned player
        """
        player = self.get_unassigned_player()
        if player:
            player.assign_client(socket, client_address)
            return player
        else:
            return False

    def get_unassigned_player(self):
        """Get a player with unassigned client
        """
        for player in self.players:
            if not self.players[player].has_client():
                return self.players[player]
        return False

    def close_connections(self):
        """Close server's socket
        """
        self.logger.debug("Closing server socket")
        self.socket.close()

    ##################
    # INITIALIZATION #
    ##################
    def initialize_game(self):
        """Initialization of the game

        Attributes
        ----------
        board : Board
        players : list of Player
        players_order : list of int
        """
        generator = BoardGenerator()
        self.board = Board(generator.generate_board())

        self.players = {}
        for i in range(1, self.number_of_players + 1):
            self.players[i] = Player(i)

        self.players_order = list(range(1, self.number_of_players + 1))
        random.shuffle(self.players_order)

        self.set_first_player()
        self.logger.debug("Player order {0}".format(self.players_order))

        self.assign_areas_to_players()
        self.assign_dice_to_players()
        self.logger.debug("Board initialized")

    def assign_areas_to_players(self):
        """Assigns areas to players at the start of the game
        """
        no_areas = len(self.board.areas)
        no_players = len(self.players)
        areas = list(range(1, no_areas + 1))

        while True:
            for player in reversed(self.players_order):
                area_name = random.choice(areas)
                area = self.board.get_area_by_name(area_name)
                self.assign_area(area, self.players[player])
                areas.remove(area_name)

                if not areas:
                    return

    def assign_dice_to_players(self):
        """Assigns dice to players at the start of the game
        """
        dice_total = 3 * self.board.get_number_of_areas() - random.randint(0, 5)
        players = len(self.players)
        players_processed = 0

        for player in reversed(self.players_order):
            dice = int(round(dice_total/ (players - players_processed)))
            dice_total -= dice

            areas = []
            for area in self.players[player].get_areas():
                areas.append(area)

            # each area has to have at least one die
            for area in areas:
                area.set_dice(1)
                dice -= 1

            while dice and areas:
                area = random.choice(areas)
                if not area.add_die(): # adding a die to area failed means that area is full
                    areas.remove(area)
                else:
                    dice -= 1

            players_processed += 1

