#!/usr/bin/python3
import sys
from subprocess import Popen
from time import sleep
from threading import Timer

from argparse import ArgumentParser
parser = ArgumentParser(prog='Dice_Wars')
parser.add_argument('-n', '--number-of-players', help="Number of players", type=int, default=2)
parser.add_argument('-p', '--port', help="Server port", type=int, default=5005)
parser.add_argument('-a', '--address', help="Server address", default='127.0.0.1')
parser.add_argument('--ai', help="Specify multiple AI versions as a sequence of ints.",
                    type=int, nargs='+')


def kill_procs(procs):
    for p in procs:
        p.kill()


def check_procs(procs):
    for p in procs:
        if p.poll() is not None:
            kill_procs(procs)
            return False
    return True


def main():
    args = parser.parse_args()

    ai_versions = [1] * (args.number_of_players - 1)
    if args.ai:
        if len(args.ai) + 1 > args.number_of_players:
            print("Too many AI versions.")
            exit(1)
        for i in range(0, len(args.ai)):
            ai_versions[i] = args.ai[i]

    procs = []

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

    procs[0].wait()
    for p in procs:
        p.kill()
        
    sys.exit(0)


if __name__ == '__main__':
    main()
