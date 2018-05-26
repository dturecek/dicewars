#!/usr/bin/env python3
import sys
from signal import signal, SIGCHLD
from subprocess import Popen
from time import sleep
from argparse import ArgumentParser


parser = ArgumentParser(prog='Dice_Wars')
parser.add_argument('-n', '--number-of-players', help="Number of players.", type=int, default=2)
parser.add_argument('-p', '--port', help="Server port", type=int, default=5005)
parser.add_argument('-a', '--address', help="Server address", default='127.0.0.1')
parser.add_argument('--ai', help="Specify AI versions as a sequence of ints.",
                    type=int, nargs='+')

procs = []


def signal_handler(signum, frame):
    """Handler for SIGCHLD signal that terminates server and clients
    """
    for p in procs:
        try:
            p.kill()
        except ProcessLookupError:
            pass


def main():
    """
    Run the Dice Wars game.

    Example:
        ./dicewars.py -n 4 --ai 4 2 1 
        # runs a four-player game with AIs 4, 2, and 1
    """
    args = parser.parse_args()
    ai_versions = [1] * (args.number_of_players - 1)

    signal(SIGCHLD, signal_handler)

    if args.ai:
        if len(args.ai) + 1 > args.number_of_players:
            print("Too many AI versions.")
            exit(1)
        for i in range(0, len(args.ai)):
            ai_versions[i] = args.ai[i]

    try:
        cmd = [
            "./server/server.py",
            "-n", str(args.number_of_players),
            "-p", str(args.port),
            "-a", str(args.address),
        ]

        procs.append(Popen(cmd))

        for i in range(1, args.number_of_players + 1):
            if i == 1:
                cmd = [
                    "./client/client.py",
                    "-p", str(args.port),
                    "-a", str(args.address),
                ]
            else:
                cmd = [
                    "./client/client.py",
                    "-p", str(args.port),
                    "-a", str(args.address),
                    "--ai", str(ai_versions[i - 2]),
                ]

            procs.append(Popen(cmd))
            sleep(0.1)

        for p in procs:
            p.wait()

    except KeyboardInterrupt:
        for p in procs:
            p.kill()


if __name__ == '__main__':
    main()
