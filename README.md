# Dice Wars

To run this, you need to have python3 and the following python packages:

    hexutil
    pyqt

To play the game, use the ``run.py`` script with the following options:

    -n    number of players, could be 2-8 with 2 being the default value
    -p    port, default 5005
    -a    address, default is localhost
    --ai  list of ai versions to play against (possible values 1-4, default 1)

Example:

    ./run.py -n 4 --ai 4 2 1  # run a 4-player game against ai versions 4, 2 and 1
