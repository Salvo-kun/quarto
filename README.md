# quarto
Project aiming at realizing a competitive player for the board game Quarto. Made for Computational Intelligence's course (A.Y. 2022/2023).


# Table of Contents
- [Collaboration](#collaboration)
- [Usage](#usage)
- [Method](#method)
    - [Bounded-depth MinMax with fail-soft alpha-beta pruning](#bounded-depth-minmax-with-fail-soft-alpha-beta-pruning)
    - [Heuristic: Quarticity](#heuristic-quarticity)
    - [Randomness](#randomness)
- [Experiments](#experiments)
    - [ProPlayer vs RandomPlayer](#proplayer-vs-randomplayer)
    - [ProPlayer vs ProPlayer](#proplayer-vs-proplayer)
    - [ProPlayer vs MinMaxPlayer](#proplayer-vs-minmaxplayer)
    - [Further comments on the bound value](#further-comments-on-the-bound-value)
- [References](#references)


# Collaboration
All work was done in collaboration with: 
* Maria Rosa Scoleri    (s301841)
* Jonathan Damone       (s301514)


# Usage
The chosen competitive player is based on MinMax with fail-soft alpha-beta pruning<sup>[1](#references)</sup>, bounded depth, randomness (only on the first move) and an heuristic called Quarticity <sup>[2](#references)</sup>.
The player can be initialized as follows, being in the main folder:

```
from quarto.players import ProPlayer
from quarto.objects import Quarto

game = Quarto()
player = ProPlayer(game) 
```

Two additional parameters can be passed to the constructor:
-   bound: a value between 1 and 3, both included. It is the type of bound the minmax will apply. 1 corresponds to fixed depth, 2 is a fixed depth = 1 except for when the bound_value is lower than the current board status complexity (in that case, depth bound is removed), 3 is a combination of the two (explore as deep as possible without evaluating more combinations than allowed in bound_value)
- bound_value: it is the value of the bound and it can assume different meaning. 

The default values are bound = 3 and bound_value = (5!)^2. This configuration achieved more than 99% of victories against a random player, with a maximum duration of a move of less than 4 seconds (1000 games were evaluated, half of them starting first and the other half starting second).

Other two players are provided: a RandomPlayer and a MinMaxPlayer. The former plays randomly, while the latter is a copy of the ProPlayer except that it does not explore states, i.e. no randomness is added to the first move.


# Method
In this section, a detailed overview of the choices made related to the player's logic is provided.

## Bounded-depth MinMax with fail-soft alpha-beta pruning
The basic block of the chosen strategy is MinMax. However, since the game has a complexity which grows as the square of the factorial of the remaining pieces to be placed, a plain version of MinMax is not feasible.
Two solutions are proposed: pruning and bounding the depth of the search tree.

The used pruning is fail-soft alpha-beta pruning<sup>[1](#references)</sup>. Alpha-Beta pruning is often combined with MinMax since it provides a cut-off of useless branches which higly reduces the complexity. The fail-soft term represents a variant introduced by John P. Fishburn in 1983, which guarantees not to cut-off potentially useful branches (not guaranteed by the fail-hard variant). This variant was preferred since it theoretically explores all interesting branches and it does not slow down the search in a considerable way.

The bounded-depth is necessary due to the fact that, even with pruning, the entire search tree is not explorable in a feasible time. The game has a complexity of 16!<sup>2</sup>, i.e. 4.4 * 10<sup>26</sup>, which becomes 4.4 * 10<sup>13</sup> with pruning. Thus, a bound is required in the early stages of the game, where the search is irrealistic. Notice that the search starts to be affordable when only 5/6 pieces are left to be placed, i.e. it is almost impossible to fully explore the game tree before 10/11 pieces are placed. Three strategies were used for bounding the search:
-   bound = 1, the bound is fixed at every turn regardless of the complexity of the game at that point of the match. The bound value is the maximum depth we want the tree to achieve.
-   bound = 2, the bound is variable based on the game's tree complexity at the current turn. The bound value is the maximum complexity (i.e. visitable states) we want to allow the MinMax to visit. The bound varies as follows: if the tree can be fully explored (i.e. the complexity is lower or equal than the bound_value), the search is full. Otherwise, the maximum depth is fixed to 1. 
-   bound = 3, the bound is again variable, but it is evaluated in a different way. The bound value is again the maximum complexity (i.e. visitable states) we want to allow the MinMax to visit. The bound varies as follows: the maximum depth is equal to the highest number of levels we can explore in the tree without evaluating more states than the maximum ones (bound_value). This is the same as the previous version when the game complexity at a given turn is lower than the maximum states allowed, but it differs from that when this is not true (i.e. in those cases the depth can be >= 1, according to the chosen bound_value). 

The varying-depth versions (i.e. bound = 2 or bound = 3), change the maximum depth at each turn through the function ```tweak_depth```, which behaves like this:
-   bound = 2, the maximum depth is not set (math.inf) if the complexity is lower than the bound_value, otherwise is set to 1. The complexity is calculated through an auxiliary static function ```estimate_tree_complexity```, which returns a worst-case complexity based on the missing pieces to be placed.
-   bound = 3, the maximum depth is the maximum between 1 (if bound_value is too low) and the result of an auxiliary static function ```find_depth```, which returns the maximum number of levels whose full explorations leads to a number of visited states lower than bound_value.

## Heuristic: Quarticity
The chosen heuristic is based on the nature of the game. In Quarto!, the winner is the first player placing four pieces on a row, column, or diagonal (forming a quarto) with at least one common characteristic. Starting from here and following the idea by D. Castro Silva and V. Vinhas<sup>[2](#references)</sup>, an efficient heuristic to determine the "power" of a state not fully explored is based on "terzo". A terzo is a 
configuration of three pieces on a row, column, or diagonal with at least one common characteristic. 

Notice that, considering at most one terzo per line (row, column or diagonal), there can be at most 10 terzos in a given board configuration (4 rows, 4 columns, 2 diagonals).

A move is thus evaluated according to these procedure:
-   if it leads to a 100% winning state, it obtains an absolute value of 12
-   if it leads to a 100% draw state, it obtains an absolute value of 11
-   otherwise it obtains an absolute value between 0 and 10 (endpoints included), according to how many terzo are present in the board

Notice that these values are "absolute" since, in MinMax, one player is minimizing while the other is maximizing, so the sign will be chosen accordingly to the current player.

A side note must be done for the value of a certain draw, i.e. 11. This value has been chosen because it is preferred to do a move which certainly does not lead to a loss rather than a move which is not certain (i.e. when its value is decided by the heuristic because the subtree cannot be fully explored). This is a conservative choice based on the decision of minimizing losses whenever possible.

## Randomness
The MinMax algorithm is a very powerful tool, but it comes with a fixed schema, i.e. given a fixed input, the output will not change. We could say, in other terms, it lacks of exploration. Following the lead of the balance between exploration and exploitation borrowed from genetic programming, there is a situation where the addition of randomness results in a stronger MinMax version.

More specifically, when the game starts, with the parameters found experimentally (see [Experiments](#experiments)), the first move is always fixed and not based on a meaningful evaluation. If the MinMax starts playing, it will always choose 0 as first piece, while if it start placing it will always choose (0,0) as first position. 
This is due to the fact that, given a bound_value of 5!<sup>2</sup> (equal to max_depth = 2, when no piece is placed), all the explored states have the same heuristic value 0 (since it is not possible to obtain a "quarto" or a "terzo" with two moves) and the algorithm will return the first option of the list since there is not a dominant best move.

The trick here is to choose randomly the first piece and to place randomly the first piece on a spot in one of the two diagonals (more chances to form quarto or terzo, hence faster games).

This slight variation proved to be beneficial, since it wins against another MinMax without exploration (we will see it in the following section).


# Experiments
In this section, we provide a rich comparison of the champion player against other players. In all the experiments the number of matches is split into two: half of them are played as first player and the other half is played as second player. Each evaluation provides:
-   Stats (Win/Loss/Draw)
-   Average and maximum duration (in seconds) of the player's move
-   Average duration (in turns) of a match

## ProPlayer vs RandomPlayer
In this subsection we compare the three possible configurations of ProPlayer against the RandomPlayer. The comparison is based on 1000 matches. 

-   ProPlayer with bound = 1 and bound_value = 1 vs RandomPlayer:
    -   Results:        {'win': 925, 'loss': 57, 'draw': 18} (Win rate: 92.5%)
    -   Turn timing:    { 'select': 0.011 s, 'place': 0.046 s } on average, { 'select': 0.153 s, 'place': 0.152 s } max
    -   Match timing:   9.724 turns on average

-   ProPlayer with bound = 2 and bound_value = 6!<sup>2</sup> vs RandomPlayer:
    -   Results:        {'win': 968, 'loss': 19, 'draw': 13} (Win rate: 96.8%)
    -   Turn timing:    { 'select': 0.010 s, 'place': 0.285 s } on average, { 'select': 0.150 s, 'place': 17.241 s } max
    -   Match timing:   10.212 turns on average

-   ProPlayer with bound = 3 and bound_value = 5!<sup>2</sup> vs RandomPlayer:
    -   Results:        {'win': 993, 'loss': 4, 'draw': 3} (Win rate: 99.3%)
    -   Turn timing:    { 'select': 0.012 s, 'place': 0.414 s } on average, { 'select': 0.153 s, 'place': 4.157 s } max
    -   Match timing:   8.726 turns on average

Based on these results, the chosen player is ProPlayer with bound = 3 and bound_value = 5!<sup>2</sup>, since it achieves the best performance against RandomPlayer with a move made in few seconds (less than 5 s). 

## ProPlayer vs ProPlayer
In this subsection we compare the chosen ProPlayer configuration against the other two. The comparison is based on 100 matches. 

-   ProPlayer with bound = 3 and bound_value = 5!<sup>2</sup> vs ProPlayer with bound = 1 and bound_value = 1:
    -   Results:        {'win': 96, 'loss': 2, 'draw': 2} (Win rate: 96%)
    -   Turn timing:    { 'select': 0.011 s, 'place': 0.490 s } on average, { 'select': 0.162 s, 'place': 2.622 s } max
    -   Match timing:   9.36 turns on average

-   ProPlayer with bound = 3 and bound_value = 5!<sup>2</sup> vs ProPlayer with bound = 2 and bound_value = 6!<sup>2</sup>:
    -   Results:        {'win': 87, 'loss': 10, 'draw': 3} (Win rate: 87%)
    -   Turn timing:    { 'select': 0.010 s, 'place': 0.486 s } on average, { 'select': 0.110 s, 'place': 2.656 s } max
    -   Match timing:   9.34 turns on average

The chosen player still outperforms the other configurations of ProPlayer, enforcing the strength of the designated champion. 

## ProPlayer vs MinMaxPlayer
In this subsection we compare the chosen ProPlayer configuration against its MinMax counterpart (i.e. no randomness). The comparison is based on 100 matches.

-   ProPlayer with bound = 3 and bound_value = 5!<sup>2</sup> vs MinMaxPlayer with bound = 3 and bound_value = 5!<sup>2</sup>:
    -   Results:        {'win': 39, 'loss': 15, 'draw': 46} (Win rate: 39%)
    -   Turn timing:    { 'select': 0.007 s, 'place': 0.518 s } on average, { 'select': 0.132 s, 'place': 2.634 s } max
    -   Match timing:   14.24 turns on average

Here it is proven that the absence of randomness hinders the results, hence preferring a ProPlayer vs a MinMaxPlayer. Notice the high number of average turns: this confirms the players are similar in terms of strength, since many of the matches cannot be won early.

## Further comments on the bound value
In order to motivate the decision of the parameters of the best player, here is reported a comparison against its enhanced version with higher bound_value. The test was run for 20 matches due to the high computation time.

-   ProPlayer with bound = 3 and bound_value = 5!<sup>2</sup> vs MinMaxPlayer with bound = 3 and bound_value = 6!<sup>2</sup>:
    -   Results:        {'win': 6, 'loss': 5, 'draw': 9} (Win rate: 30%)
    -   Turn timing:    { 'select': 0.007 s, 'place': 0.432 s } on average, { 'select': 0.149 s, 'place': 1.805 } max
    -   Match timing:   13.8 turns on average

-   ProPlayer with bound = 3 and bound_value = 5!<sup>2</sup> vs ProPlayer with bound = 3 and bound_value = 6!<sup>2</sup>:
    -   Results:        {'win': 4, 'loss': 14, 'draw': 2} (Win rate: 20%)
    -   Turn timing:    { 'select': 0.008 s, 'place': 0.538 s } on average, { 'select': 0.103 s, 'place': 2.606 s } max
    -   Match timing:   11.7 turns on average

We can see that the chosen player is not the best one, but it can still win sometimes. However, the new best player is way slower as we can see from the stats of the next comparison.

-   ProPlayer with bound = 3 and bound_value = 6!<sup>2</sup> vs MinMaxPlayer with bound = 3 and bound_value = 6!<sup>2</sup>:
    -   Results:        {'win': 16, 'loss': 2, 'draw': 2} (Win rate: 80%)
    -   Turn timing:    { 'select': 0.232 s, 'place': 6.212 s } on average, { 'select': 3.067 s, 'place': 44.555 s } max
    -   Match timing:   13.8 turns on average

These are respectively the strongest ProPlayer version and the strongest MinMaxPlayer version which it was possible to run on an average computer (i.e. in a reasonable time). We can see that the turn duration, in the worst case, is more than 40 s, which is not acceptable (our goal was few seconds).

In conclusion, our chosen player is: ProPlayer with bound = 3 and bound_value = 5!<sup>2</sup>.


# References
1.  [John P. Fishburn. 1983. Another optimization of alpha-beta search. SIGART Bull., 84 (April 1983), 37–38.](https://doi.org/10.1145/1056623.1056628)

2.  [Daniel Castro Silva and Vasco Vinhas, A flexible extended Quarto! implementation based on combinatorial analysis, IADIS International Conference Gaming 2008](https://web.fe.up.pt/~niadr/PUBLICATIONS/2008/Gaming2008_DCS_VVM.pdf)
