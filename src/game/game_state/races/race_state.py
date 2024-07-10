"""
This module contains the RaceState class
"""
from overrides import overrides
from abc import abstractmethod

from src.engine.components.transform import Transform
from src.engine.managers.input_manager.key import Key
from src.game.entities.tile import Tile
from src.game.game_state.game_states_enum import StateEnum
from src.game.game_state.igame_state import IGameState
from src.game.map.map_types import MapType


class RaceState(IGameState):
    """
    This is an abstract class to inherit from to reuse the code of race states
    It handles the initialization and part of the update and destruction of the state
    """
    def __init__(self, game, state_enum):
        super().__init__(game, state_enum)

    def initialize_race(self, number_of_cars: int) -> None:
        """
        This must be called in the initialize method of the child class
        It will initialize the game and the cars and the car manager.
        :param number_of_cars:
        :return:
        """
        self._game.start_game()
        self._game.get_cars_manager().set_number_of_cars(number_of_cars)
        self._create_cars()
        self._game.get_cars_manager().initialize()

    def _handle_go_to_menu_input(self) -> None:
        """
        This handles the common input of the racing scenes to go to the menu
        :return: None
        """
        if self._game.get_input_manager().is_key_down(Key.K_ESCAPE):
            self._game.set_game_state(StateEnum.MENU)

    @abstractmethod
    def initialize(self):
        """
        This must be inherited and called in the initialize method of the child class
        :return:
        """
        pass

    @abstractmethod
    def update(self, delta_time) -> None:
        """
        This must be inherited and called in the update method of the child class
        This class moves the camera, reduces the velocity of the cars in the sidewalk and grass and handles the input
        to go to the menu
        :param delta_time:
        :return:
        """
        self._game.move_camera()
        self._handle_go_to_menu_input()
        for car in self._game.get_cars_manager().get_cars():
            car_entity_id = car.entity_ID
            car_physics = self._game.get_entity_manager().get_physics(car_entity_id)
            car_transform: Transform = self._game.get_entity_manager().get_transform(car.entity_ID)
            tile_of_car: Tile = self._game.get_tile_map().get_tile_at_pos_vec(car_transform.get_position())
            if tile_of_car.tile_type == MapType.SIDEWALK or tile_of_car.tile_type == MapType.GRASS:
                car_physics.set_velocity(car_physics.get_velocity() * 0.9)

    @abstractmethod
    def render(self) -> None:
        """
        This must be inherited by the child class
        Does nothing
        :return:
        """
        pass

    @abstractmethod
    def render_debug(self) -> None:
        """
        This must be inherited by the child class
        Does nothing
        :return:
        """
        pass

    @overrides
    def destruct(self) -> None:
        """
        This will clear the game
        Must be inherited by the child class
        :return:
        """
        self._game.game_clear()

    @abstractmethod
    def _create_cars(self) -> None:
        """
        This must be inherited by the child class
        Does nothing
        The child classes must inherit this method and create the custom cars for their respective game.
        :return:
        """
        pass
