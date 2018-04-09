from argparse import ArgumentParser

parser = ArgumentParser(prog='Dice_Wars-server')
parser.add_argument('-n', '--number-of-players', help="Number of players", type=int, default=2)
parser.add_argument('-p', '--port', help="Server port", type=int, default=5005)
parser.add_argument('-a', '--address', help="Server address", default='127.0.0.1')
parser.add_argument('-d', '--debug', help="Enable debug output", default='WARN')
parser.add_argument('-v', '--verbose', help="Collect data about game progress", action='store_true')


def parse():
    args = parser.parse_args()
    if args.debug.lower() == 'debug':
        logging = 10
    elif args.debug.lower() == 'info':
        logging = 20
    elif args.debug.lower() == 'error':
        logging = 40
    else:
        logging = 30

    return args, logging
