import random
import time

import pygame
from pygame import Vector2, Rect

from engine.engine import Engine
from engine.engine_attributes import EngineAttributes
from engine.engine_fonts import EngineFonts
from engine.managers.input_manager.key import Key
from game.ai.ai_manager import AIManager
from game.game_mode import GameMode
from game.game_state.game_state import GameState
from game.entities.NPC import NPC
from game.entities.car import Car
from game.map.tile_map import TileMap


class Game(Engine):
    def __init__(self):
        super().__init__()
        self.game_mode: GameMode = GameMode.AI_TRAINING
        self.play_music("GameMusic")

        self.cars: list[Car] = []
        self.tile_map: TileMap = TileMap(self)
        self.NPCs: list[NPC] = []

        self.ai_manager: AIManager = AIManager(self._initialize_cars, self.game_mode == GameMode.AI_TRAINING)

        self._initialize()

        # self._initialize_cars()
        # self._initialize_npcs()

    def _initialize(self):
        self._initialize_cars()
        self._initialize_npcs()

    def _initialize_cars(self):
        # self.camera.reset_position()

        if len(self.cars) == 0:
            if self.game_mode == GameMode.MANUAL or self.game_mode == GameMode.AI_PLAYING:
                self.cars.append(Car(self.create_entity("entities/car", has_collider=True, is_static=False)))
            elif self.game_mode == GameMode.AI_TRAINING:
                for i in range(self.ai_manager.get_population_size()):
                    self.cars.append(Car(self.create_entity("entities/car", has_collider=True, is_static=False,
                                                            is_training=True)))

        for car in self.cars:
            # Vector2(11 * 16, 42 * 16)
            # index=y×width+x
            map_width = self.tile_map.width // 16
            tile = (self.tile_map.tiles[11 + 42 * map_width].tile_entity.get_transform().get_position())
            car.set_position(Vector2(tile[0], tile[1]))
        # print(self.cars[0].car_entity.get_transform().get_position())
        # print(self.camera.get_position())

    def update(self, delta_time):
        for car in self.cars:
            car.field_of_view.update(car.car_entity, self.tile_map, [npc.NPC_entity for npc in self.NPCs])
            checkpoint: int = self.tile_map.get_checkpoint_in(car.field_of_view.get_tiles_in_FOV())
            car.reach_checkpoint(checkpoint)
            distance_to_next_checkpoint = self.tile_map.get_distance_to_next_checkpoint(
                checkpoint,
                (car.car_entity.get_transform().get_position()[0], car.car_entity.get_transform().get_position()[1]))
            if distance_to_next_checkpoint is not None:
                car.set_distance_to_next_checkpoint(distance_to_next_checkpoint)
            type_tile = car.field_of_view.get_nearest_tile().tile_type
            car.set_current_tile_type(type_tile)
            if checkpoint is not None:
                car.traveled_distance = checkpoint * 10

        super().update(delta_time)

        self.move_camera()

        # self.game_state.update(self.car.car_entity)
        if self.game_mode is GameMode.AI_TRAINING or self.game_mode is GameMode.AI_PLAYING:
            self.ai_manager.update(self.cars)  # ([car.car_entity for car in self.cars])

        i = 0
        for car in self.cars:
            if self.game_mode is GameMode.MANUAL:  # or i == 0:
                car.update_input(self.input_manager)
            elif self.game_mode is GameMode.AI_TRAINING or self.game_mode is GameMode.AI_PLAYING:
                ai_input_manager = self.ai_manager.get_ai_input_manager_of(car)
                car.update_input(ai_input_manager)
            car.update(delta_time)
            i += 1

    def game_render_debug(self):
        for car in self.cars:
            vision = car.car_entity.get_transform().get_position()
            vision_rect = Rect(vision.x - 96, vision.y - 96, 192, 192)
            self.renderer.draw_rect(vision_rect, (255, 0, 0), 3)

            self._render_field_of_view(car)

    # def _select_agents(self):
        # before selecting agents, delete previous rectangles, redrawing game?

        # pygame.display.flip()
        # time.sleep(3)
        # for car in self.cars:
        #     car.selected_as_parent = False

    def game_render(self):
        if self.game_mode == GameMode.AI_TRAINING:
            self.renderer.draw_surface(
                    EngineFonts.get_fonts().debug_UI_font.render
                    (f"Generation number: {self.ai_manager.genetic_algorithm.get_generation_number()}",
                     True, EngineAttributes.DEBUG_FONT_COLOR), Vector2(0, 30))
        selected = False
        for car in self.cars:
            if car.selected_as_provisional_parent:
                self.renderer.draw_rect(car.car_entity.get_sprite_rect(), (255, 0, 0), 3)
                selected = True
                car.selected_as_provisional_parent = False
            elif car.selected_as_parent:
                self.renderer.draw_rect(car.car_entity.get_sprite_rect(), (0, 255, 0), 3)
                # selected = True
                car.selected_as_parent = False
        if selected:
            pygame.display.flip()
            # Wait 2 seconds
            time.sleep(2)
    #     for car in self.cars:
    #         if car.selected_as_parent:
    #             self.renderer.draw_rect(car.car_entity.get_sprite_rect(), (0, 255, 0), 3)

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

        car_position = self.cars[0].car_entity.get_transform().get_position()
        camera_position = -self.camera.get_position() + Vector2(self.window.get_width(), self.window.get_height())
        difference = camera_position - car_position
        if difference.length() > 1:
            self.camera.move(difference)

    def follow_player(self):
        # Define the "box" dimensions within which the camera doesn't need to move
        camera_box_width = self.window.get_width() / 5
        camera_box_height = self.window.get_height() / 5

        # Calculate the distance from the car to the camera
        # TODO: The camera should follow the first car (best fitness)
        distance_to_box = self.cars[0].car_entity.get_transform().get_position() - self.camera.get_position()

        # Check if the car is outside the "box" area
        if abs(distance_to_box.x) > camera_box_width or abs(distance_to_box.y) > camera_box_height:
            # Move the camera by the distance needed to re-center the car
            self.camera.move(-distance_to_box)

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

    def restore_previous_state(self, game_state: GameState):
        self.game_state = game_state

    def _render_field_of_view(self, car: Car):
        field_of_view = car.field_of_view.get()
        for tile, npc in field_of_view:
            if tile is not None:
                if npc == 0:
                    self.renderer.draw_rect(tile.tile_entity.get_sprite_rect(), (255, 0, 0), 1)
                elif npc == 1:
                    self.renderer.draw_rect(tile.tile_entity.get_sprite_rect(), (0, 0, 255), 1)

    def _change_input_manager_to_AI(self):
        if self.game_mode is GameMode.AI_TRAINING:
            self.input_manager = self.ai_manager.ai_input_manager
