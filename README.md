# quarto
Project aiming at realizing a competitive player for the board game Quarto. Made for Computational Intelligence's course (A.Y. 2022/2023).

## Collaboration
All work was done in collaboration with: 
* Maria Rosa Scoleri    (s301841)
* Jonathan Damone       (s301514)

## Usage
The competitive player is based on MinMax with alpha-beta pruning, bounded depth and heuristic.
The player can be initialized as follows, being in the main folder:

```
from quarto.players import MinMaxPlayer
from quarto.objects import Quarto

game = Quarto()
player = MinMaxPlayer(game) 

```

Two additional parameters can be passed to the constructor:
-   bound: a value between 1 and 3, both included. It is the type of bound the minmax will apply. 1 corresponds to fixed depth, 2 is a fixed depth = 1 except for when the bound_value is lower than the current board status complexity (in that case, depth bound is removed), 3 is a combination of the two (explore as deep as possible without evaluating more combinations than allowed in bound_value)
- bound_value: it is the value of the bound and it can assume different meaning. 

The default values are bound = 3 and bound_value = (6!)^2. This configuration achieved 99.6% of victories against a random player, with a maximum duration of a move of less than 4 seconds (1000 games were evaluated, half of them starting first and the other half starting second).