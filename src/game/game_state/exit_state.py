"""
This module contains the ExitState class
"""
from overrides import overrides

from src.game.game_state.igame_state import IGameState
from src.game.game_state.game_states_enum import StateEnum


class ExitState(IGameState):
    """
    This is the state that will be used to exit the game
    When this state is active the game will exit
    """
    def __init__(self, game, state_enum: StateEnum):
        super().__init__(game, state_enum)

    @overrides
    def initialize(self):
        """
        On initialize the game will exit
        :return:
        """
        self._game.exit_running()

    @overrides
    def update(self, delta_time):
        pass

    @overrides
    def render(self):
        pass

    @overrides
    def render_debug(self):
        pass

    @overrides
    def destruct(self):
        pass
