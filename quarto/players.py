# Free for personal or classroom use; see 'LICENSE.md' for details.
# https://github.com/squillero/computational-intelligence

from copy import deepcopy
from enum import Enum
import math
from .objects import Quarto, Player
from .extensions import Extensions
import random
from functools import reduce
from operator import and_

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

    class MinMaxBound(Enum):
        FIXED_DEPTH = 1
        FIXED_COMPLEXITY = 2
        VARIABLE_COMPLEXITY = 3

    WIN_SCORE = 12
    DRAW_SCORE = 11

    def __init__(self, quarto: Quarto, bound: int = 3, bound_value: int = math.factorial(6) ** 2) -> None:
        super().__init__(quarto)
        self.best_move = None
        self.max_depth = None
        self.max_combs = None
        self.__set_bound(bound, bound_value)


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

    def __set_bound(self, bound: MinMaxBound, bound_value: int):
        if bound == self.MinMaxBound.FIXED_DEPTH.value:
            self.max_depth = bound_value
        elif bound == self.MinMaxBound.FIXED_COMPLEXITY.value: 
            self.max_combs = bound_value
        elif bound == self.MinMaxBound.VARIABLE_COMPLEXITY.value: 
            self.max_combs = bound_value
        else:
            raise ValueError(f'Invalid bound type: {bound}. Choose between {[e.value for e in self.MinMaxBound]}')

        self.bound = bound

    def __tweak_depth(self, game: Quarto) -> None:
        if self.bound == self.MinMaxBound.FIXED_COMPLEXITY.value: 
            self.max_depth = math.inf if Extensions.estimate_tree_complexity(game) <= self.max_combs else 1
        elif self.bound == self.MinMaxBound.VARIABLE_COMPLEXITY.value: 
            self.max_depth = Extensions.find_depth(sum(sum(game.get_board_status() == -1)), self.max_combs)            

    def __heuristic(self, state: Quarto):
        score = 0
        board = state.get_board_status()

        for row in board:
            useful_pieces = row != -1
            if sum(useful_pieces) == 3:
                if reduce(and_, row[useful_pieces]) != 0 or reduce(and_, map(Extensions.bitwise_not_wrapper(4), row[useful_pieces])) != 0:
                    score += 1                

        for col in board.T:
            useful_pieces = col != -1
            if sum(useful_pieces) == 3:
                if reduce(and_, col[useful_pieces]) != 0 or reduce(and_, map(Extensions.bitwise_not_wrapper(4), col[useful_pieces])) != 0:
                    score += 1

        for diag in [board.diagonal(), board[::-1].diagonal()]:
            useful_pieces = diag != -1
            if sum(useful_pieces) == 3:
                if reduce(and_, diag[useful_pieces]) != 0 or reduce(and_, map(Extensions.bitwise_not_wrapper(4), diag[useful_pieces])) != 0:
                    score += 1        
        
        return -score if state.get_current_player() == self.get_game().get_current_player() else score

    def __minmax(self, state: Quarto, alpha, beta, depth=0):
        if depth >= self.max_depth:
            return self.__heuristic(state), None    
        
        available_pieces = list(i for i in range(state.BOARD_SIDE ** 2) if i not in state.get_board_status() and i != state.get_selected_piece())
        available_positions = list((j % state.BOARD_SIDE, j // state.BOARD_SIDE) for j in range(state.BOARD_SIDE ** 2) if state.get_board_status()[j // state.BOARD_SIDE][j % state.BOARD_SIDE] < 0)
        # print(f'{available_pieces} at depth {depth}') if depth == 0 else None
        # print(f'{available_positions} at depth {depth}') if depth == 0 else None

        if state.get_current_player() == self.get_game().get_current_player(): # my turn, minimize
            value = (math.inf, ((math.inf, math.inf), math.inf))
            for x, y in available_positions:
                middle_state = deepcopy(state)

                if middle_state.get_selected_piece() not in middle_state.get_board_status() and middle_state.get_selected_piece() != -1:
                    # print(f'Placing {middle_state.get_selected_piece()} at {(y, x)} at depth {depth}')
                    assert middle_state.place(x, y), 'Error placing'
                
                    winner = middle_state.check_winner()  
                    if middle_state.check_finished() or winner != -1:
                        if winner == -1:
                            score = -MinMaxPlayer.DRAW_SCORE
                        else:
                            winner = 1 - winner if self.get_game().get_current_player() == 1 else winner
                            score = -MinMaxPlayer.WIN_SCORE if winner == 0 else MinMaxPlayer.WIN_SCORE
                        value = min(value, (score, ((x, y), -1)))

                        if value <= alpha:
                            break

                        beta = min(beta, value)
                        # print(f'Score: {score} at depth {depth}')
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
                            score = MinMaxPlayer.DRAW_SCORE
                        else:
                            winner = 1 - winner if self.get_game().get_current_player() == 1 else winner
                            score = -MinMaxPlayer.WIN_SCORE if winner == 0 else MinMaxPlayer.WIN_SCORE
                        value = max(value, (score, ((x, y), -1)))
                    
                        if value >= beta:
                            break
                        
                        alpha = max(alpha, value) 
                        # print(f'Score: {score} at depth {depth}')
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
