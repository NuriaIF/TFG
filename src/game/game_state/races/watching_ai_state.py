"""
This module contains the WatchingAIState class
"""
from overrides import overrides
from pygame import Vector2

from src.engine.components.transform import Transform
from src.engine.ai.AI_input_manager import AIInputManager
from src.game.ai.ai_manager import AIManager
from src.game.ai.explainability.explainability_manager import ExplainabilityManager
from src.game.entities.car import Car
from src.game.entities.tile import Tile
from src.game.game_state.races.race_state import RaceState


class WatchingAIState(RaceState):
    """
    This is the state of the game of watching AI
    In this state the trained AI plays by itself and does not train
    """
    @overrides
    def initialize(self) -> None:
        """
        Initialize the watching AI state, it creates one car entity
        :return: None
        """
        super().initialize_race(1)
        self._game.get_cars_manager().set_ai_manager(AIManager(self._game.get_entity_manager(), training=False))
        self._game.set_explainability_manager(ExplainabilityManager(self._game.renderer))

    @overrides
    def update(self, delta_time) -> None:
        """
        Update the watching AI state by updating the cars and the AI.
        :param delta_time:
        :return: None
        """
        cars = self._game.get_cars_manager().get_cars()
        i: int
        car: Car
        for i, car in enumerate(cars):
            car_transform: Transform = self._game.get_entity_manager().get_transform(car.entity_ID)
            tile_of_car: Tile = self._game.get_tile_map().get_tile_at_pos_vec(car_transform.get_position())

            self._game.get_cars_manager().handle_ai_knowledge(car, tile_of_car)

            car.update_input()
            car.update(delta_time)
        self._game.get_cars_manager().get_ai_manager().update(cars, self._game.get_input_manager(),
                                                              self._game.get_chronometer())
        super().update(delta_time)

    @overrides
    def render(self) -> None:
        """
        This renders the state of the watching AI
        It renders the explainability of the AI, including the inputs and outputs of the neural network
        :return: None
        """
        if len(self._game.get_cars_manager().get_ai_manager().get_agents()) == 0:
            return
        agent = self._game.get_cars_manager().get_ai_manager().get_agents()[0]
        if len(agent.neural_network.inputs) == 0:
            return
        neural_network = agent.neural_network
        inputs = neural_network.inputs
        outputs = neural_network.outputs
        self._game.get_explainability_manager().render_explainability(inputs, outputs)

    @overrides
    def render_debug(self) -> None:
        """
        This renders the debug information of the watching AI state
        It renders the checkpoints and the car knowledge
        :return: None
        """
        for car in self._game.get_cars_manager().get_cars():
            self._game.get_debug_renderer().draw_text_absolute(
                f"Checkpoint number: {car.car_knowledge.checkpoint_number}",
                Vector2(100, 0), (255, 255, 255))
            self._game.get_debug_renderer().draw_text_absolute(
                f"Traveled distance: {car.car_knowledge.traveled_distance}",
                Vector2(100, 20), (255, 255, 255))

    @overrides
    def _create_cars(self) -> None:
        """
        Create the car for the watching AI state
        :return: None
        """
        entity = self._game.get_cars_manager().create_car_entity()
        self._game.get_cars_manager().add_car(Car(entity, self._game.get_entity_manager(), AIInputManager()))
