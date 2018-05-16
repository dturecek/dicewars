# Dice Wars

Dice Wars is a strategy game where players take turns to attack adjacent territories to expand
their area. Each territory contains a number of dice determining player's presence
and strength. The objective of the game is to conquer all territories and thus eliminate each opponent.

This is a client-server implementation that was created as a part of my bachelor's thesis
where it is described in more detail.

## Usage

To use this, you need to have python3 and the following python packages:

    hexutil
    numpy
    pyqt

To play the game, use the ``dicewars.py`` script with the following options:

    -n    number of players, could be 2-8 with 2 being the default value
    -p    port, default 5005
    -a    address, default is localhost
    --ai  list of ai versions to play against (possible values 1-4, default 1)

Example:

    ./dicewars.py -n 4 --ai 4 2 1  # run a 4-player game against ai versions 4, 2 and 1

## List of AI players
#### Naive (AI 1)
This agent performs all possible moves in random order

#### Strength Difference Checking (AI 2)
This agent prefers moves with highest strength difference 
and doesn't make moves against areas with higher strength.

#### Single Turn Expectiminimax (AI 3)
This agent makes such moves that have a probability of successful
attack and hold over the area until next turn higher than 20 %.

#### Improved Single Turn Expectiminimax (AI 4)
This agent makes such moves that have a probability of successful
attack and hold over the area until next turn higher a 20% in two-player
games and higher than 40% in four-player games. In addition, it prefers 
attacks initiated from its largest region.

#### Win Probability Maximization using Scores (AI 5)
This agent estimates win probability given the current state of the game.
As a feature to describe the state, a vector of players' scores is used.
The agent choses such moves, that will have the highest improvement in
the estimated probability.

#### Win Probability Maximization using Dice (AI 6)
This agent estimates win probability given the current state of the game.
As a feature to describe the state, a vector of logarithms of players' scores
is used. The agent choses such moves, that will have the highest improvement
in the estimated probability.

#### Win Probability Maximization using Scores and Dice (AI 7)
This agent estimates win probability given the current state of the game.
As a feature to describe the state, a vector of logarithms of players' dice
and scores is used. The agent choses such moves, that will have the highest
improvement in the estimated probability.

