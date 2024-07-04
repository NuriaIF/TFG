from overrides import overrides
from pygame import Vector2

from src.engine.components.transform import Transform
from src.game.entities.car import Car
from src.game.entities.tile import Tile
from src.game.game_state.races.irace_state import IRaceState

class PlayingState(IRaceState):
    @overrides
    def initialize(self):
        super().initialize_race(1)

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
        super().update(delta_time)

    @overrides
    def render(self):
        pass

    @overrides
    def render_debug(self):
        self._game.render_checkpoints()
        self._game.get_cars_manager().render_car_knowledge()

        for car in self._game.get_cars_manager().get_cars():
            self._game.get_debug_renderer().draw_text_absolute(
                f"Checkpoint number: {car.car_knowledge.checkpoint_number}",
                Vector2(100, 0), (255, 255, 255))

    @overrides
    def _create_cars(self):
        entity = self._game.get_cars_manager().create_car_entity()
        self._game.get_cars_manager().add_car(
            Car(entity, self._game.get_entity_manager(), self._game.get_input_manager()))
