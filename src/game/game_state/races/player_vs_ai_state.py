"""
This module contains the PlayerVsAIState class.
"""
from overrides import overrides
from pygame import Vector2

from src.engine.components.transform import Transform
from src.engine.ai.AI_input_manager import AIInputManager
from src.game.ai.ai_manager import AIManager
from src.game.entities.car import Car
from src.game.entities.tile import Tile
from src.game.game_state.races.race_state import RaceState


class PlayerVsAIState(RaceState):
    """
    This is the state of the game of player vs. AI
    In this state the trained AI plays against the player
    """
    @overrides
    def initialize(self):
        """
        Initialize the player vs. AI state, it creates two car entities
        :return:
        """
        super().initialize_race(2)
        self._game.get_cars_manager().set_ai_manager(AIManager(self._game.get_entity_manager(), training=False))

    @overrides
    def update(self, delta_time):
        """
        Update the player vs. AI state by updating the cars and the AI.
        The AI gives the input to the AI cars and the player gives the input to the player car
        :param delta_time:
        :return:
        """
        cars = self._game.get_cars_manager().get_cars()
        i: int
        car: Car
        for i, car in enumerate(cars):
            car_transform: Transform = self._game.get_entity_manager().get_transform(car.entity_ID)
            tile_of_car: Tile = self._game.get_tile_map().get_tile_at_pos_vec(car_transform.get_position())

            self._game.get_cars_manager().handle_car_out_of_bounds(car, tile_of_car)

            self._game.get_cars_manager().handle_ai_knowledge(car, tile_of_car)

            car.update_input()
            car.update(delta_time)
        ai_cars = [cars[1]]
        self._game.get_cars_manager().get_ai_manager().update(ai_cars, self._game.get_input_manager(),
                                                              self._game.get_chronometer())
        super().update(delta_time)

    @overrides
    def render(self):
        """
        This renders the text that marks the player and the AI to be able to differentiate them
        :return:
        """
        car_player_position = self._game.get_entity_manager().get_transform(
            self._game.get_cars_manager().get_cars()[0].entity_ID).get_position()
        car_ai_position = self._game.get_entity_manager().get_transform(
            self._game.get_cars_manager().get_cars()[1].entity_ID).get_position()

        self._game.debug_renderer.draw_text("Player", car_player_position, (255, 255, 255), centered=True)
        self._game.debug_renderer.draw_text("AI", car_ai_position, (255, 255, 255), centered=True)

    @overrides
    def render_debug(self):
        """
        This renders the debugging information for the player vs. AI state
        Will render the checkpoint number of the player and the AI
        Checkpoints are the tiles that the cars have to pass through
        :return:
        """
        cars = self._game.get_cars_manager().get_cars()
        self._game.get_debug_renderer().draw_text_absolute(
            f"Checkpoint number (AI): {cars[1].car_knowledge.checkpoint_number}",
            Vector2(300, 0), (255, 255, 255))
        self._game.get_debug_renderer().draw_text_absolute(
            f"Checkpoint number (Player): {cars[0].car_knowledge.checkpoint_number}",
            Vector2(300, 20), (255, 255, 255))

    @overrides
    def _create_cars(self):
        """
        This creates all the cars for the player vs. AI state
        :return:
        """
        entity = self._game.get_cars_manager().create_car_entity()
        self._game.get_cars_manager().add_car(Car(entity, self._game.get_entity_manager(),
                                                  self._game.get_input_manager()))
        entity = self._game.get_cars_manager().create_car_entity()
        self._game.get_cars_manager().add_car(Car(entity, self._game.get_entity_manager(), AIInputManager()))
