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
        return random.choice(list(i for i in range(self.get_game().BOARD_SIDE ** 2) if i not in self.get_game().get_board_status() and i != self.get_game().get_selected_piece()))
        # return random.randint(0, 15)

    def place_piece(self) -> tuple[int, int]:
        return random.choice(list((j % self.get_game().BOARD_SIDE, j // self.get_game().BOARD_SIDE) for j in range(self.get_game().BOARD_SIDE ** 2) if self.get_game().get_board_status()[j // self.get_game().BOARD_SIDE][j % self.get_game().BOARD_SIDE] < 0))
        # return random.randint(0, 3), random.randint(0, 3)

class MinMaxPlayer(Player):
    """MinMax player"""

    def __init__(self, quarto: Quarto, max_depth=math.inf, max_combs=None) -> None:
        super().__init__(quarto)
        self.max_depth = max(max_depth, 1)
        self.best_move = None
        self.max_combs = max_combs

    def choose_piece(self) -> int:
        if not self.best_move:
            self.__tweak_depth(self.get_game())
            self.best_move = self.__minmax(self.get_game(), (-math.inf, ((-math.inf, -math.inf), -math.inf)), (math.inf, ((math.inf, math.inf), math.inf)), 0)

        # print(f'Choosing... Best move: {self.best_move}')
        m = self.best_move[1][1]
        self.best_move = None
        return m

    def place_piece(self) -> tuple[int, int]:
        if not self.best_move:
            self.__tweak_depth(self.get_game())     
            self.best_move = self.__minmax(self.get_game(), (-math.inf, ((-math.inf, -math.inf), -math.inf)), (math.inf, ((math.inf, math.inf), math.inf)), 0)

        # print(f'Placing... Best move: {self.best_move}')
        return self.best_move[1][0]

    @staticmethod
    def __estimate_tree_complexity(game: Quarto):
        return math.factorial(sum(sum(game.get_board_status() == -1))) ** 2

    def __tweak_depth(self, game: Quarto) -> None:
        if self.max_combs:
            self.max_depth = math.inf if MinMaxPlayer.__estimate_tree_complexity(game) <= self.max_combs else self.max_depth

    def __minmax(self, state: Quarto, alpha, beta, depth=0):
        if depth >= self.max_depth:
            return 0.5, None    
        
        available_pieces = list(i for i in range(state.BOARD_SIDE ** 2) if i not in state.get_board_status() and i != state.get_selected_piece())
        available_positions = list((j % state.BOARD_SIDE, j // state.BOARD_SIDE) for j in range(state.BOARD_SIDE ** 2) if state.get_board_status()[j // state.BOARD_SIDE][j % state.BOARD_SIDE] < 0)
        # print(f'{available_pieces} at depth {depth}') if depth == 0 else None
        # print(f'{available_positions} at depth {depth}') if depth == 0 else None

        if Extensions.get_current_player(state) == Extensions.get_current_player(self.get_game()): # my turn, minimize
            value = (math.inf, ((math.inf, math.inf), math.inf))
            for x, y in available_positions:
                middle_state = deepcopy(state)

                if middle_state.get_selected_piece() not in middle_state.get_board_status() and middle_state.get_selected_piece() != -1:
                    # print(f'Placing {middle_state.get_selected_piece()} at {(y, x)} at depth {depth}')
                    assert middle_state.place(x, y), 'Error placing'
                
                    winner = middle_state.check_winner()  
                    if middle_state.check_finished() or winner != -1:
                        if winner == -1:
                            winner = 0.5
                        val = 1 - winner if Extensions.get_current_player(self.get_game()) == 1 else winner
                        value = min(value, (val, ((x, y), -1)))

                        if value <= alpha:
                            break

                        beta = min(beta, value)
                        # print(f'Winner: {winner} at depth {depth}')
                        continue   

                for p in available_pieces:
                    new_state = deepcopy(middle_state)
                    assert new_state.select(p), 'Error selecting'
                    Extensions.end_player_turn(new_state)
                    val, _ = self.__minmax(new_state, alpha, beta, depth + 1)
                    # print(f'Move {(val, ((y, x), p))} at depth {depth}')
                    value = min(value, (val, ((x, y), p)))

                    if value <= alpha:
                        break

                    beta = min(beta, value)   
            return value
        else: # its turn, maximize
            value = (-math.inf, ((-math.inf, -math.inf), -math.inf))
            for x, y in available_positions:
                middle_state = deepcopy(state)

                if middle_state.get_selected_piece() not in middle_state.get_board_status() and middle_state.get_selected_piece() != -1:
                    # print(f'Placing {middle_state.get_selected_piece()} at {(y, x)} at depth {depth}')
                    assert middle_state.place(x, y), 'Error placing'
                
                    winner = middle_state.check_winner()  
                    if middle_state.check_finished() or winner != -1:
                        if winner == -1:
                            winner = 0.5
                        val = 1 - winner if Extensions.get_current_player(self.get_game()) == 1 else winner
                        value = max(value, (val, ((x, y), -1)))
                    
                        if value >= beta:
                            break
                        
                        alpha = max(alpha, value) 
                        # print(f'Winner: {winner} at depth {depth}')
                        continue
                    
                for p in available_pieces:
                    new_state = deepcopy(middle_state)
                    assert new_state.select(p), 'Error selecting'
                    Extensions.end_player_turn(new_state)
                    val, _ = self.__minmax(new_state, alpha, beta, depth + 1)
                    # print(f'Move {(val, ((y, x), p))} at depth {depth}')
                
                    value = max(value, (val, ((x, y), p)))
                    
                    if value >= beta:
                        break

                    alpha = max(alpha, value) 
            return value
