from abc import ABC, abstractmethod

from src.game.game_state.game_states_enum import StateEnum


class IGameState(ABC):
    def __init__(self, game: 'Game', state_enum: StateEnum):
        self._other_states: set[StateEnum] = set()
        self._game: 'Game' = game
        self._state_enum = state_enum

    def link_to_state(self, state_enum: StateEnum) -> None:
        self._other_states.add(state_enum)

    def get_state_enum(self) -> StateEnum:
        return self._state_enum

    def can_change_to_state(self, state_enum: 'GameEnum'):
        return state_enum in self._other_states

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def destruct(self):
        pass

    @abstractmethod
    def update(self, delta_time: float):
        pass

    @abstractmethod
    def render(self):
        pass

    @abstractmethod
    def render_debug(self):
        pass
