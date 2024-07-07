from overrides import overrides
from pygame import Vector2

from src.engine.components.transform import Transform
from src.engine.ai.AI_input_manager import AIInputManager
from src.game.ai.ai_manager import AIManager, population_size
from src.game.entities.car import Car
from src.game.entities.tile import Tile
from src.game.game_state.races.race_state import RaceState


class TrainingState(RaceState):
    @overrides
    def initialize(self):
        super().initialize_race(population_size)
        self._game.get_cars_manager().set_ai_manager(AIManager(self._game.get_entity_manager(), training=True))
        self._game.get_chronometer().start()

    @overrides
    def update(self, delta_time):
        if self._game.get_cars_manager().get_ai_manager().has_generation_ended():
            self._game.reset()
            self._game.get_cars_manager().get_ai_manager().next_generation()
        self._update_cars(delta_time)
        super().update(delta_time)

    def render(self):
        self._game.debug_renderer.draw_text_absolute(
            "Generation: " + str(self._game.get_cars_manager().get_ai_manager().genetic_algorithm.current_generation),
            Vector2(100, 0),
            (255, 255, 255))

    @overrides
    def render_debug(self):
        # for car in self.game.get_cars_manager().get_cars():
        # if car.selected_as_parent:
        #     sprite_rect = self._entity_manager.get_sprite_rect(car.entity_ID)
        #     self._debug_renderer.draw_rect(sprite_rect, (0, 0, 255), 3)
        #     car.selected_as_parent = False

        sorted_list = sorted(self._game.get_cars_manager().get_ai_manager().get_agents(), key=lambda x: x.fitness_score, reverse=True)
        agent_with_best_fitness = sorted_list[0]
        self._game.get_debug_renderer().draw_rect_absolute(
            self._game.get_entity_manager().get_sprite_rect(agent_with_best_fitness.controlled_entity.entity_ID), (0, 255, 0),
            3)
        for car in self._game.get_cars_manager().get_cars():
            # self._game.get_debug_renderer().draw_text(
            #     f"Checkpoint number: {car.car_knowledge.checkpoint_number}",
            #     self._game.get_entity_manager().get_transform(car.entity_ID).get_position(), (255, 255, 255))
            self._game.get_debug_renderer().draw_text(
                f"Traveled distance: {car.car_knowledge.traveled_distance}",
                self._game.get_entity_manager().get_transform(car.entity_ID).get_position(), (255, 255, 255))


    @overrides
    def _create_cars(self):
        for i in range(self._game.get_cars_manager().get_number_of_cars()):
            entity = self._game.get_cars_manager().create_car_entity()
            self._game.get_cars_manager().add_car(Car(entity, self._game.get_entity_manager(), AIInputManager()))

    def _update_cars(self, delta_time: float):
        cars = self._game.get_cars_manager().get_cars()
        i: int
        car: Car
        for i, car in enumerate(cars):
            car_transform: Transform = self._game.get_entity_manager().get_transform(car.entity_ID)
            tile_of_car: Tile = self._game.get_tile_map().get_tile_at_pos_vec(car_transform.get_position())

            self._game.get_cars_manager().handle_ai_knowledge(car, tile_of_car)

            self._game.get_cars_manager().handle_ai_training(car, tile_of_car)

            car.update_input()
            car.update(delta_time)
        self._game.get_cars_manager().get_ai_manager().update(cars, self._game.get_input_manager(),
                                                              self._game.get_chronometer())