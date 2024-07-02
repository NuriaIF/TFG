from overrides import overrides
from pygame import Vector2

from engine.components.transform import Transform
from game.AI.AI_input_manager import AIInputManager
from game.AI.AI_manager import AIManager
from game.entities.car import Car
from game.entities.tile import Tile
from game.game_state.races.irace_state import IRaceState


class PlayerVsAIState(IRaceState):
    @overrides
    def initialize(self):
        super().initialize_race(2)
        self._game.get_cars_manager().set_ai_manager(AIManager(self._game.get_entity_manager(), training=False))

    @overrides
    def update(self, delta_time):
        cars = self._game.get_cars_manager().get_cars()
        i: int
        car: Car
        for i, car in enumerate(cars):
            car_transform: Transform = self._game.get_entity_manager().get_transform(car.entity_ID)
            tile_of_car: Tile = self._game.get_tile_map().get_tile_at_pos_vec(car_transform.get_position())

            self._game.get_cars_manager().handle_ai_knowledge(car, tile_of_car)

            car.update_input()
            car.update(delta_time)
        ai_cars = [cars[1]]
        self._game.get_cars_manager().get_ai_manager().update(ai_cars, self._game.get_input_manager(),
                                                              self._game.get_chronometer())
        super().update(delta_time)

    @overrides
    def render(self):
        car_player_position = self._game.get_entity_manager().get_transform(
            self._game.get_cars_manager().get_cars()[0].entity_ID).get_position()
        car_ai_position = self._game.get_entity_manager().get_transform(
            self._game.get_cars_manager().get_cars()[1].entity_ID).get_position()

        self._game.debug_renderer.draw_text("Player", car_player_position, (255, 255, 255), centered=True)
        self._game.debug_renderer.draw_text("AI", car_ai_position, (255, 255, 255), centered=True)

    @overrides
    def render_debug(self):
        cars = self._game.get_cars_manager().get_cars()
        self._game.get_debug_renderer().draw_text_absolute(
            f"Checkpoint number (AI): {cars[1].car_knowledge.checkpoint_number}",
            Vector2(300, 0), (255, 255, 255))
        self._game.get_debug_renderer().draw_text_absolute(
            f"Checkpoint number (Player): {cars[0].car_knowledge.checkpoint_number}",
            Vector2(300, 20), (255, 255, 255))

    @overrides
    def _create_cars(self):
        entity = self._game.get_cars_manager().create_car_entity()
        self._game.get_cars_manager().add_car(Car(entity, self._game.get_entity_manager(), self._game.get_input_manager()))
        entity = self._game.get_cars_manager().create_car_entity()
        self._game.get_cars_manager().add_car(Car(entity, self._game.get_entity_manager(), AIInputManager()))
