# Free for personal or classroom use; see 'LICENSE.md' for details.
# https://github.com/squillero/computational-intelligence

import copy
from .objects import Quarto

class Extensions():
    @staticmethod
    def get_current_player(state: Quarto) -> int:
        '''
        Get the current player
        '''
        return copy.deepcopy(state._Quarto__current_player)

    @staticmethod
    def end_player_turn(state: Quarto) -> int:
        '''
        Pass the turn to the next player
        '''
        state._Quarto__current_player = (state._Quarto__current_player + 1) % state.MAX_PLAYERS