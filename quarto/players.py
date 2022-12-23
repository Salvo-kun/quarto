# Free for personal or classroom use; see 'LICENSE.md' for details.
# https://github.com/squillero/computational-intelligence

from copy import deepcopy
import logging
import math
from quarto import Quarto, Player
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

    def __init__(self, quarto: Quarto, max_depth=math.inf) -> None:
        super().__init__(quarto)
        self.max_depth = max_depth
        self.best_move = None
        self.max_depth = max_depth

    def choose_piece(self) -> int:
        if not self.best_move:
            self.best_move = self.minmax_with_pruning(self.get_game(), (-math.inf, None), (math.inf, None), 0)[1]

        m = self.best_move[1]
        self.best_move = None
        return m

    def place_piece(self) -> tuple[int, int]:
        if not self.best_move:
            self.best_move = self.minmax_with_pruning(self.get_game(), (-math.inf, None), (math.inf, None), 0)[1]
        return self.best_move[0]

    def minmax_with_pruning(self, state: Quarto, alpha, beta, depth=0):
        winner = state.check_winner()  
        if state.check_finished() or winner != -1:
            loser = 1 - 2 * winner
            return loser, None 

        if depth >= self.max_depth:
            return 0, None        
        
        available_pieces = list(i for i in range(state.BOARD_SIDE ** 2) if i not in state.get_board_status() and i != state.get_selected_piece())
        available_positions = list((j % 4, j // 4) for j in range(state.BOARD_SIDE ** 2) if state.get_board_status()[j // 4][j % 4] < 0)

        #logging.warning(f'Depth: {depth} Player: {state.get_current_player()} Pieces: {available_pieces} Positions: {available_positions} Board: {state.get_board_status()}')

        if state.get_current_player() == self.get_game().get_current_player(): # my turn, minimize
            value = (math.inf, (available_positions[0], None))
            for x, y in available_positions:
                tmp = deepcopy(state)

                if tmp.get_selected_piece() not in tmp.get_board_status() and tmp.get_selected_piece() != -1:
                    assert tmp.place(x, y), 'Error placing'

                for p in available_pieces:
                    tmp2 = deepcopy(tmp)
                    assert tmp2.select(p), 'Error selecting'
                    tmp2.end_player_turn()
                    val, _ = self.minmax_with_pruning(tmp2, alpha, beta, depth + 1)

                    # logging.warning(f'Move: {(val, ((x, y), p))} by player at depth {depth}')
                    
                    value = min(value, (val, ((x, y), p)))

                    if value <= alpha:
                        break
                        # return value  # To check if it is okay to break two cycles at once

                    beta = min(beta, value)   
            return value
        else: # its turn, maximize
            value = (-math.inf, (available_positions[0], None))
            for x, y in available_positions:
                tmp = deepcopy(state)

                if tmp.get_selected_piece() not in tmp.get_board_status() and tmp.get_selected_piece() != -1:
                    assert tmp.place(x, y), 'Error placing'
                    
                for p in available_pieces:
                    tmp2 = deepcopy(tmp)
                    assert tmp2.select(p), 'Error selecting'
                    tmp2.end_player_turn()
                    val, _ = self.minmax_with_pruning(tmp2, alpha, beta, depth + 1)

                    # logging.warning(f'Move: {(val, ((x, y), p))} by opponent at depth {depth}')
                
                    value = max(value, (val, ((x, y), p)))
                    
                    if value >= beta:
                        break
                        # return value  # To check if it is okay to break two cycles at once

                    alpha = max(alpha, value) 

            return value

    

