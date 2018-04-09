import json
from json.decoder import JSONDecodeError
import logging

class GenericAI(object):
    def __init__(self, game, verbose):
        self.logger = logging.getLogger('AI')
        self.game = game
        self.board = game.board
        self.player_name = game.player_name
        self.waitingForResponse = False
        self.verbose = verbose
        self.ai_version = 0

    def run(self):
        game = self.game

        while True:
            message = game.input_queue.get(block=True, timeout=None)
            try:
                if not self.handle_server_message(json.loads(message)):
                    exit(0)
            except JSONDecodeError:
                self.logger.error("Invalid message from server.")
                exit(1)
            self.current_player_name = game.current_player.get_name()
            if self.current_player_name == self.player_name and not self.waitingForResponse:
                self.ai_turn()

    def ai_turn(self):
        return True

    def handle_server_message(self, msg):
        self.logger.debug("Received message type {0}.".format(msg["type"]))
        if msg['type'] == 'battle':
            atk_data = msg['result']['atk']
            def_data = msg['result']['def']
            attacker = self.game.board.get_area(str(atk_data['name']))
            attacker.set_dice(atk_data['dice'])
            atk_name = attacker.get_owner_name()

            defender = self.game.board.get_area(def_data['name'])
            defender.set_dice(def_data['dice'])
            def_name = defender.get_owner_name()

            if def_data['owner'] == atk_data['owner']:
                defender.set_owner(atk_data['owner'])
                self.game.players[atk_name].set_score(msg['score'][str(atk_name)])
                self.game.players[def_name].set_score(msg['score'][str(def_name)])

            self.waitingForResponse = False

        elif msg['type'] == 'end_turn':
            current_player = self.game.players[self.game.current_player_name]
            #current_player.set_reserve(msg['reserve'])

            for area in msg['areas']:
                owner_name = msg['areas'][area]['owner']
                owner = self.game.players[owner_name]

                area_object = self.game.board.get_area(int(area))

                area_object.set_owner(owner_name)
                area_object.set_dice(msg['areas'][area]['dice'])

            current_player.deactivate()
            self.game.current_player_name = msg['current_player']
            self.game.current_player = self.game.players[msg['current_player']]
            self.game.players[self.game.current_player_name].activate()
            self.waitingForResponse = False

        elif msg['type'] == 'game_end':
            self.logger.info("Player {} has won".format(msg['winner']))
            self.game.socket.close()
            return False

        elif msg['type'] == 'game_state' and self.verbose:
            print("Gathering some data")
            print(msg)
        return True

    def send_message(self, type, attacker=None, defender=None):
        if type == 'close':
            msg = {'type': 'close'}
        elif type == 'battle':
            msg = {
                'type': 'battle',
                'atk': attacker,
                'def': defender
            }
        elif type == 'end_turn':
            msg = {'type': 'end_turn'}
            self.logger.debug("Sending end_turn message.")

        msg['ai'] = self.ai_version

        try:
            self.game.socket.send(str.encode(json.dumps(msg)))
        except BrokenPipeError:
            self.logger.error("Connection to server broken.")
            exit(1)
