# Free for personal or classroom use; see 'LICENSE.md' for details.
# https://github.com/squillero/computational-intelligence

import copy
import math
from .objects import Quarto

class Extensions():
    @staticmethod
    def end_player_turn(state: Quarto) -> int:
        '''
        Pass the turn to the next player
        '''
        state._current_player = (state._current_player + 1) % state.MAX_PLAYERS

    @staticmethod
    def estimate_tree_complexity(game: Quarto):
        return math.factorial(sum(sum(game.get_board_status() == -1))) ** 2

    @staticmethod
    def find_depth(remaining_turns, max_complexity):
        product = 1
        for i, v in enumerate(range(remaining_turns, 0, -1)):
            product *= v**2
            if product > max_complexity:
                return i
        return remaining_turns
