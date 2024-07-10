"""
This module contains the interface for the game states
"""
from abc import ABC, abstractmethod

from src.game.game_state.game_states_enum import StateEnum


class IGameState(ABC):
    """
    This is the interface that all the game states must implement
    """
    def __init__(self, game: 'Game', state_enum: StateEnum):
        self._other_states: set[StateEnum] = set()
        self._game: 'Game' = game
        self._state_enum = state_enum

    def link_to_state(self, state_enum: StateEnum) -> None:
        """
        This tells the state what other states it can change to.
        :param state_enum:
        :return:
        """
        self._other_states.add(state_enum)

    def get_state_enum(self) -> StateEnum:
        """
        Get the state enum
        :return: The state enum of the state
        """
        return self._state_enum

    def can_change_to_state(self, state_enum: StateEnum) -> bool:
        """
        Checks if this state can change to the state given
        :param state_enum:
        :return:
        """
        return state_enum in self._other_states

    @abstractmethod
    def initialize(self):
        """
        Initialize the game state
        """
        pass

    @abstractmethod
    def destruct(self):
        """
        Destruct the game state
        """
        pass

    @abstractmethod
    def update(self, delta_time: float):
        """
        Update the game state
        :param delta_time: The time since the last frame
        """
        pass

    @abstractmethod
    def render(self):
        """
        Render the game state
        """
        pass

    @abstractmethod
    def render_debug(self):
        """
        Render the debug information of the game state
        """
        pass
