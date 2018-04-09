from argparse import ArgumentParser

parser = ArgumentParser(prog='Dice_Wars-client')
parser.add_argument('-p', '--port', help="Server port", type=int, default=5005)
parser.add_argument('-a', '--address', help="Server address", default='127.0.0.1')
parser.add_argument('-d', '--debug', help="Enable debug output", default='WARN')
parser.add_argument('--ai', help="Ai version", type=int)
parser.add_argument('-v', '--verbose', help="Used for gathering game data", action='store_true')


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
