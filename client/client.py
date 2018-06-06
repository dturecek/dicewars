#!/usr/bin/env python3
import logging
from importlib import import_module
from PyQt5.QtWidgets import QApplication
import sys

from args import parse
from game import Game
from ui import ClientUI


def main():
    """Client side of Dice Wars
    """
    args, log_level = parse()
    logging.basicConfig(level=log_level)
    logger = logging.getLogger('CLIENT')

    game = Game(args.address, args.port)

    if args.ai:
        if args.ai == 1:
            from ai.ai1 import AI
        elif args.ai == 2:
            from ai.ai2 import AI
        elif args.ai == 3:
            from ai.ai3 import AI
        elif args.ai == 4:
            from ai.ai4 import AI
        elif args.ai == 5:
            from ai.ai5 import AI
        elif args.ai == 6:
            from ai.ai6 import AI
        elif args.ai == 7:
            from ai.ai7 import AI
        else:
            logging.error("No AI version {0}.".format(args.ai))
            exit(1)

        ai = AI(game)
        ai.run()

    else:
        app = QApplication(sys.argv)
        ui = ClientUI(game)
        sys.exit(app.exec_())


if __name__ == '__main__':
    main()
