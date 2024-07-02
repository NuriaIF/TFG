from overrides import overrides

from game.game_state.igame_state import IGameState
from game.game_state.game_states_enum import StateEnum


class ExitState(IGameState):
    def __init__(self, game, state_enum: StateEnum):
        super().__init__(game, state_enum)


    @overrides
    def initialize(self):
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