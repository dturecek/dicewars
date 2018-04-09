#!/usr/bin/python3
import logging
from importlib import import_module
from PyQt5.QtWidgets import QApplication
import sys

from args import parse
from game import Game
from ui import ClientUI


def main():
    args, log_level = parse()
    logging.basicConfig(level=log_level)
    logger = logging.getLogger('CLIENT')

    game = Game(args.address, args.port, args.ai)

    if args.ai:
        if args.ai == 1:
            from ai.ai1 import AI
        elif args.ai == 2:
            from ai.ai2 import AI
        elif args.ai == 3:
            from ai.ai3 import AI
        elif args.ai == 4:
            from ai.ai4 import AI
        else:
            logging.error("No AI version {0}.".format(args.ai))
            exit(1)

        ai = AI(game, args.verbose)
        ai.run()

    else:
        app = QApplication(sys.argv)
        ui = ClientUI(game)
        sys.exit(app.exec_())


if __name__ == '__main__':
    main()
