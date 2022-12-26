# Free for personal or classroom use; see 'LICENSE.md' for details.
# https://github.com/squillero/computational-intelligence

from copy import deepcopy
import math
from .objects import Quarto, Player
from .extensions import Extensions
import random

class RandomPlayer(Player):
    """Random player"""

    def __init__(self, quarto: Quarto) -> None:
        super().__init__(quarto)

    def choose_piece(self) -> int:
        return random.randint(0, 15)

    def place_piece(self) -> tuple[int, int]:
        return random.randint(0, 3), random.randint(0, 3)

class MinMaxPlayer(Player):
    """MinMax player"""

    def __init__(self, quarto: Quarto, max_depth=math.inf, max_combs=None) -> None:
        super().__init__(quarto)
        self.max_depth = max(max_depth, 1)
        self.best_move = None
        self.max_combs = max_combs

    def choose_piece(self) -> int:
        if not self.best_move:
            self.best_move = self.__minmax(self.get_game(), (-math.inf, ((-math.inf, -math.inf), -math.inf)), (math.inf, ((math.inf, math.inf), math.inf)), 0)[1]

        m = self.best_move[1]
        self.best_move = None
        return m

    def place_piece(self) -> tuple[int, int]:
        if not self.best_move:
            self.best_move = self.__minmax(self.get_game(), (-math.inf, ((-math.inf, -math.inf), -math.inf)), (math.inf, ((math.inf, math.inf), math.inf)), 0)[1]
        return self.best_move[0]

    @staticmethod
    def __estimate_tree_complexity(remaining_positions, remaining_pieces):
        return math.factorial(remaining_positions) * math.factorial(remaining_pieces)

    def __tweak_depth(self, remaining_positions, remaining_pieces) -> None:
        if self.max_combs:
            self.max_depth = max(1, self.max_combs // MinMaxPlayer.__estimate_tree_complexity(remaining_positions, remaining_pieces))

    def __minmax(self, state: Quarto, alpha, beta, depth=0):
        winner = state.check_winner()  
        if state.check_finished() or winner != -1:
            loser = 1 - 2 * winner
            return loser, None 

        if depth >= self.max_depth:
            return 0, None        
        
        available_pieces = list(i for i in range(state.BOARD_SIDE ** 2) if i not in state.get_board_status() and i != state.get_selected_piece())
        available_positions = list((j % state.BOARD_SIDE, j // state.BOARD_SIDE) for j in range(state.BOARD_SIDE ** 2) if state.get_board_status()[j // state.BOARD_SIDE][j % state.BOARD_SIDE] < 0)

        self.__tweak_depth(len(available_positions), len(available_positions))

        if Extensions.get_current_player(state) == Extensions.get_current_player(self.get_game()): # my turn, minimize
            value = (math.inf, (available_positions[0], math.inf))
            for x, y in available_positions:
                middle_state = deepcopy(state)

                if middle_state.get_selected_piece() not in middle_state.get_board_status() and middle_state.get_selected_piece() != -1:
                    assert middle_state.place(x, y), 'Error placing'

                for p in available_pieces:
                    new_state = deepcopy(middle_state)
                    assert new_state.select(p), 'Error selecting'
                    Extensions.end_player_turn(new_state)
                    val, _ = self.__minmax(new_state, alpha, beta, depth + 1)
                    
                    value = min(value, (val, ((x, y), p)))

                    if value <= alpha:
                        break

                    beta = min(beta, value)   
            return value
        else: # its turn, maximize
            value = (-math.inf, (available_positions[0], -math.inf))
            for x, y in available_positions:
                middle_state = deepcopy(state)

                if middle_state.get_selected_piece() not in middle_state.get_board_status() and middle_state.get_selected_piece() != -1:
                    assert middle_state.place(x, y), 'Error placing'
                    
                for p in available_pieces:
                    new_state = deepcopy(middle_state)
                    assert new_state.select(p), 'Error selecting'
                    Extensions.end_player_turn(new_state)
                    val, _ = self.__minmax(new_state, alpha, beta, depth + 1)
                
                    value = max(value, (val, ((x, y), p)))
                    
                    if value >= beta:
                        break

                    alpha = max(alpha, value) 

            return value

    

