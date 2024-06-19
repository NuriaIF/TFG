import math
import time

import pygame
from pygame import Vector2

from engine.engine import Engine
from engine.engine_attributes import EngineAttributes
from engine.engine_fonts import EngineFonts
from engine.managers.input_manager.key import Key
from game.ai.ai_manager import AIManager
from game.game_mode import GameMode
from game.entities.NPC import NPC
from game.entities.car import Car
from game.map.map_types import MapType
from game.map.tile_map import TileMap
from interpretability_and_explainability.explainability_and_interpretability import ExplainabilityAndInterpretability


class Game(Engine):
    def __init__(self):
        super().__init__()
        self.game_mode: GameMode = GameMode.AI_TRAINING

        # self.play_music("GameMusic")

        self.cars: list[Car] = []
        self.tile_map: TileMap = TileMap(self, self.entity_manager)
        self.NPCs: list[NPC] = []

        self.ai_manager: AIManager = AIManager(self._initialize_cars, self.entity_manager,
                                               self.game_mode == GameMode.AI_TRAINING)

        self._initialize()

        self.better_fitness_index = []

        self.explainability_and_interpretability = None

    def _initialize(self):
        self._initialize_cars()
        self._initialize_npcs()

    def _initialize_cars(self):
        if len(self.cars) == 0:
            if self.game_mode == GameMode.MANUAL or self.game_mode == GameMode.AI_PLAYING:
                self.cars.append(Car(self.create_entity("entities/car", has_collider=True, is_static=False),
                                     self.entity_manager))
            elif self.game_mode == GameMode.AI_TRAINING:
                for i in range(self.ai_manager.get_population_size()):
                    self.cars.append(Car(self.create_entity("entities/car", has_collider=True, is_static=False,
                                                            is_training=True), self.entity_manager))

        map_width = self.tile_map.width // 16
        tile_id = self.tile_map.tiles[(11 + 8) + (42 + 8) * map_width].entity_ID
        start_tile = self.entity_manager.get_transform(tile_id).get_position()

        for car in self.cars:
            # self.entity_manager.reset_entities()
            car.reset()
            self.entity_manager.get_transform(car.entity_ID).set_position(Vector2(start_tile[0], start_tile[1]))
            # car.set_position(Vector2(start_tile[0], start_tile[1]))
        if self.game_mode == GameMode.AI_TRAINING:
            self.ai_manager.reset(self.cars)

    def update(self, delta_time):
        for car in self.cars:
            fov = car.car_knowledge.field_of_view
            car_transform = self.entity_manager.get_transform(car.entity_ID)
            npc_sprite_rects = [self.entity_manager.get_sprite_rect(npc.entity_ID) for npc in self.NPCs]
            fov.update(car_transform, self.tile_map, npc_sprite_rects, self.entity_manager)
            checkpoint: int = self.tile_map.get_checkpoint_in(fov.get_checkpoint_activation_area())
            car_in_tile = fov.get_nearest_tile()
            car.car_knowledge.reach_checkpoint(checkpoint)
            next_checkpoint_position = self.tile_map.get_next_checkpoint_position(car.car_knowledge.checkpoint_number)
            car.car_knowledge.update(car_in_tile.tile_type, next_checkpoint_position,
                                     self.entity_manager.get_transform(car.entity_ID).get_forward(),
                                     self.entity_manager.get_physics(car.entity_ID).get_velocity(),
                                     self.entity_manager, car_transform)

            if checkpoint is not None:
                car.traveled_distance = checkpoint * 10

        super().update(delta_time)

        if self.game_mode is GameMode.AI_TRAINING or self.game_mode is GameMode.AI_PLAYING:
            self.ai_manager.update(self.cars, self.input_manager)  # ([car.car_entity for car in self.cars])
        if self.game_mode is GameMode.AI_PLAYING:
            if self.explainability_and_interpretability is None:
                neural_network = self.ai_manager.get_agents()[0].neural_network
                self.explainability_and_interpretability = ExplainabilityAndInterpretability(neural_network)
            self.explainability_and_interpretability.update(self.renderer, self.ai_manager.inputs)

        i = 0
        for car in self.cars:
            if self.game_mode is GameMode.MANUAL:  # or i == 0:
                car.update_input(self.input_manager)
            elif self.game_mode is GameMode.AI_TRAINING or self.game_mode is GameMode.AI_PLAYING:
                ai_input_manager = self.ai_manager.get_ai_input_manager_of(car)
                car.update_input(ai_input_manager)
            car.update(delta_time)
            i += 1

        self.move_camera()
        # if self.game_mode is GameMode.AI_TRAINING:
        #     self.better_fitness_index = []
        #     cars_aux = self.cars.copy()
        #     cars_aux.sort(key=lambda x: x.entity_ID.get_fitness(), reverse=True)
        #     self.better_fitness_index = [self.cars.index(car) for car in cars_aux]

    def game_render_debug(self):
        for car in self.cars:
            if self.game_mode == GameMode.AI_PLAYING or self.game_mode == GameMode.MANUAL:
                self._render_field_of_view(car)

                colors = [
                    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
                    (255, 0, 255), (0, 255, 255), (128, 0, 128), (128, 128, 0),
                    (0, 128, 128), (128, 0, 0), (0, 128, 0), (0, 0, 128), (128, 128, 128)
                ]
                center = Vector2(200, 200)
                i = 0
                color = colors[0]
                for vector in self.tile_map.positions:
                    # cada 12, pasar al siguiente color
                    if i % 12 == 0:
                        color = colors[i // 12]
                    self.renderer.draw_circle(center + vector, 5, color, 3)
                    self.renderer.draw_provisional_text(f"{i}", center + vector, (255, 255, 255), 10)
                    i += 1
                center = Vector2(200, 500)
                for tile, vector in zip(car.car_knowledge.field_of_view.get(), self.tile_map.positions):
                    if tile[0] is not None:
                        if tile[0].tile_type == MapType.TRACK:
                            self.renderer.draw_circle(center + vector, 5, (0, 0, 0), 5)
                        elif tile[0].tile_type == MapType.GRASS:
                            self.renderer.draw_circle(center + vector, 5, (0, 255, 0), 5)
                        elif tile[0].tile_type == MapType.SIDEWALK:
                            self.renderer.draw_circle(center + vector, 5, (155, 155, 155), 5)
                        elif tile[0].tile_type == MapType.SEA:
                            self.renderer.draw_circle(center + vector, 5, (0, 0, 255), 5)

            # checkpoint_text = f"Checkpoint: {car.checkpoint_number}"
            # distance_to_next_text = f"Distance to next: {car.distance_to_next_checkpoint}"
            # angle_to_next_text = f"Angle to next: {car.angle_to_next_checkpoint}"
            # position = car.car_entity.get_transform().get_position()
            # forward = car.car_entity.get_transform().get_forward()
            # entity_direction = f"Direction: {math.degrees(math.atan2(forward.y, forward.x))}"
            # difference_between_forward_and_angle = abs(
            #     car.angle_to_next_checkpoint - math.degrees(math.atan2(forward.y, forward.x)))
            # self.renderer.draw_text(checkpoint_text, Vector2(position[0], position[1] + 60))
            # self.renderer.draw_text(distance_to_next_text, Vector2(position[0], position[1] + 75))
            # self.renderer.draw_text(angle_to_next_text, Vector2(position[0], position[1] + 90))
            # self.renderer.draw_text(entity_direction, Vector2(position[0], position[1] + 105))
            # self.renderer.draw_text(f"Difference: {difference_between_forward_and_angle}", Vector2(position[0], position[1] + 120))

        self.game_render()

    def game_render(self):
        self._render_checkpoints()

        if self.game_mode == GameMode.AI_TRAINING:
            self.renderer.draw_surface(
                EngineFonts.get_fonts().debug_UI_font.render
                (f"Generation number: {self.ai_manager.genetic_algorithm.get_generation_number()}",
                 True, EngineAttributes.DEBUG_FONT_COLOR), Vector2(0, 50))
        selected = False

        for car in self.cars:
            if car.selected_as_parent:
                sprite_rect = self.entity_manager.get_sprite_rect(car.entity_ID)
                self.renderer.draw_rect(sprite_rect, (0, 0, 255), 3)
                selected = True
                car.selected_as_parent = False

        if selected:
            pygame.display.flip()
            # Wait 0.5 seconds
            time.sleep(0.5)
        else:
            i = 1
            for index in self.better_fitness_index:
                color = (255, 0, 0) if i > 2 else (0, 255, 0)
                # self.renderer.draw_rect(self.cars[index].car_entity.get_sprite_rect(), color, 3)
                # self.renderer.draw_provisional_text(f"Fitness: {self.cars[index].car_entity.get_fitness()}",
                #                                     self.cars[index].car_entity.get_transform().get_position(), color,
                #                                     size=10)
                # self.renderer.draw_provisional_text(f"Index: {i}", self.cars[index].car_entity.get_transform()
                #                                     .get_position() + Vector2(0, 15), color, size=10)
                i += 1
            if self.game_mode == GameMode.AI_TRAINING:
                for agent in self.ai_manager.genetic_algorithm.elitism_list:
                    sprite_rect = self.entity_manager.get_sprite_rect(agent.controlled_entity.entity_ID)
                    self.renderer.draw_rect(sprite_rect, (0, 0, 255), 3)

    def move_camera(self):
        if self.input_manager.is_key_down(Key.K_UP):
            self.camera.move(Vector2(0, -100))
        if self.input_manager.is_key_down(Key.K_DOWN):
            self.camera.move(Vector2(0, 100))
        if self.input_manager.is_key_down(Key.K_LEFT):
            self.camera.move(Vector2(-100, 0))
        if self.input_manager.is_key_down(Key.K_RIGHT):
            self.camera.move(Vector2(100, 0))

        """
        The camera follows the car, if the car leaves a box centered on the camera, the camera moves to the car's
        position
        """
        self.center_camera_on_car()

    def center_camera_on_car(self):
        # TODO: The camera should follow the first car (best fitness)
        if len(self.cars) == 1:
            car = self.cars[0]
        else:
            agents = sorted(self.ai_manager.get_agents(), key=lambda x: x.best_fitness, reverse=True)
            car = agents[0].controlled_entity
        car_position = self.entity_manager.get_transform(car.entity_ID).get_position()
        camera_position = -self.camera.get_position() + Vector2(self.window.get_width(), self.window.get_height())
        difference = camera_position - car_position
        if difference.length() > 1:
            self.camera.move(difference)

    def _initialize_npcs(self):
        self.NPCs: list[NPC] = []
        # number_of_people = 5
        # number_of_bikes = 2
        # for i in range(number_of_people):
        #     self.NPCs.append(NPC(self.create_entity("entities/person_head", has_collider=True, is_static=False)))
        #     self.NPCs[i].set_position(Vector2(random.randint(0, 100) * 16 - 8, random.randint(0, 60) * 16 - 8))
        # for j in range(number_of_people, number_of_people + number_of_bikes):
        #     self.NPCs.append(NPC(self.create_entity("entities/bicycle", has_collider=True, is_static=False)))
        #     self.NPCs[j].set_position(Vector2(random.randint(0, 100) * 16 - 8, random.randint(0, 60) * 16))

    def _render_field_of_view(self, car: Car):
        vision_box: pygame.Rect = car.car_knowledge.field_of_view.get_vision_box()
        self.renderer.draw_polygon(vision_box, (255, 0, 0), 3)
        field_of_view = car.car_knowledge.field_of_view.get()
        num = 0
        for tile, npc in field_of_view:
            if tile is not None:
                sprite_rect = self.entity_manager.get_sprite_rect(tile.entity_ID)
                transform = self.entity_manager.get_transform(tile.entity_ID)
                if npc == 0:
                    self.renderer.draw_rect(sprite_rect, (255, 0, 0), 1)
                    self.renderer.draw_circle(transform.get_position(), 2, (255, 255, 0), 1)
                elif npc == 1:
                    self.renderer.draw_rect(sprite_rect, (0, 0, 255), 1)
                if num < 10:
                    text_position = transform.get_position()
                    text_position = text_position[0] + 4, text_position[1]
                else:
                    text_position = transform.get_position()
                self.renderer.draw_provisional_text(str(num), text_position, (0, 0, 255), size=10)
            num += 1

    def _render_checkpoints(self):
        for tile in self.tile_map.checkpoints:
            sprite_rect = self.entity_manager.get_sprite_rect(tile.entity_ID)
            transform = self.entity_manager.get_transform(tile.entity_ID)
            self.renderer.draw_rect(sprite_rect, (255, 255, 0), 1)
            tile_position = transform.get_position()
            if tile.checkpoint_number < 10:
                checkpoint_text_position = tile_position[0] + 4, tile_position[1]
            else:
                checkpoint_text_position = tile_position
            self.renderer.draw_text(str(tile.checkpoint_number), checkpoint_text_position, (255, 255, 0))

