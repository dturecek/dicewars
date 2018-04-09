#!/usr/bin/python3
import logging

from args import parse
from game import Game


def main():
    args, log_level = parse()
    logging.basicConfig(level=log_level)
    logger = logging.getLogger('SERVER')
    logger.debug("Command line arguments: {0}".format(args))

    game = Game(args.number_of_players, args.address, args.port)
    game.run()


if __name__ == '__main__':
    main()
