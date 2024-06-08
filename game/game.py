import math
import time

import numpy as np
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
from game.map.map_types import MapType
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

        map_width = self.tile_map.width // 16
        start_tile = (self.tile_map.tiles[(11 + 8) + (42 + 8) * map_width].tile_entity.get_transform().get_position())

        for car in self.cars:
            car.reset()
            car.set_position(Vector2(start_tile[0], start_tile[1]))
        if self.game_mode == GameMode.AI_TRAINING:
            for agent in self.ai_manager.get_agents():
                agent.reset()
        # print(self.cars[0].car_entity.get_transform().get_position())
        # print(self.camera.get_position())

    def update(self, delta_time):
        for car in self.cars:
            car.field_of_view.update(car.car_entity, self.tile_map, [npc.NPC_entity for npc in self.NPCs])
            checkpoint: int = self.tile_map.get_checkpoint_in(car.field_of_view.get_checkpoint_activation_area())
            car.reach_checkpoint(checkpoint)
            distance_to_next_checkpoint = self.tile_map.get_distance_to_next_checkpoint(
                car.checkpoint_number,
                (car.car_entity.get_transform().get_position()[0], car.car_entity.get_transform().get_position()[1]))
            next_checkpoint_position = self.tile_map.get_next_checkpoint_position(car.checkpoint_number)
            car.set_next_checkpoint_position(next_checkpoint_position)
            angle_to_next_checkpoint = self.tile_map.get_angle_to_next_checkpoint(
                car.checkpoint_number,
                (car.car_entity.get_transform().get_position()[0], car.car_entity.get_transform().get_position()[1]))
            if distance_to_next_checkpoint is not None:
                car.set_distance_to_next_checkpoint(distance_to_next_checkpoint)
                car.set_angle_to_next_checkpoint(angle_to_next_checkpoint)
            type_tile = car.field_of_view.get_nearest_tile().tile_type
            car.set_current_tile_type(type_tile)
            if checkpoint is not None:
                car.traveled_distance = checkpoint * 10

        super().update(delta_time)

        if self.game_mode is GameMode.AI_TRAINING or self.game_mode is GameMode.AI_PLAYING:
            self.ai_manager.update(self.cars, self.input_manager)  # ([car.car_entity for car in self.cars])

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

    def rotate_point(self, point, center, angle) -> Vector2:
        angle_rad = np.deg2rad(angle)
        cos_angle = np.cos(angle_rad)
        sin_angle = np.sin(angle_rad)
        translated_point = point - center
        rotated_point = np.dot(np.array([
            [cos_angle, -sin_angle],
            [sin_angle, cos_angle]
        ]), translated_point)
        rotated_point = Vector2([rotated_point[0], rotated_point[1]])
        return rotated_point + center

    def game_render_debug(self):
        for car in self.cars:
            if self.game_mode == GameMode.AI_PLAYING or self.game_mode == GameMode.MANUAL:
                vision = car.car_entity.get_transform().get_position()
                vision_rect = Rect(vision.x - 96, vision.y - 96, 192, 192)
                # self.renderer.draw_rect(vision_rect, (255, 0, 0), 3)
                # Calculamos el centro del Rect
                center = Vector2([vision_rect.centerx, vision_rect.centery])

                # Calculamos las esquinas del Rect
                points = [
                    Vector2([vision_rect.topright[0], vision_rect.topright[1]]),
                    Vector2([vision_rect.bottomright[0], vision_rect.bottomright[1]]),
                    Vector2([vision_rect.bottomleft[0], vision_rect.bottomleft[1]]),
                    Vector2([vision_rect.topleft[0], vision_rect.topleft[1]]),
                ]
                # Angulo de rotación en grados (suponiendo que obtienes este ángulo de la dirección del coche)
                angle = np.degrees(np.arctan2(car.car_entity.get_transform().get_forward().y,
                                              car.car_entity.get_transform().get_forward().x))
                # Rotamos cada punto alrededor del centro
                rotated_points: list[Vector2] = [self.rotate_point(point, center, angle) for point in points]
                # Dibujamos el Rect rotado
                self.renderer.draw_polygon(rotated_points, (255, 0, 0), 3)
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
                for tile, vector in zip(car.field_of_view.get(), self.tile_map.positions):
                    if tile[0] is not None:
                        if tile[0].tile_type == MapType.TRACK:
                            self.renderer.draw_circle(center + vector, 5, (0, 0, 0), 5)
                        elif tile[0].tile_type == MapType.GRASS:
                            self.renderer.draw_circle(center + vector, 5, (0, 255, 0), 5)
                        elif tile[0].tile_type == MapType.SIDEWALK:
                            self.renderer.draw_circle(center + vector, 5, (155, 155, 155), 5)
                        elif tile[0].tile_type == MapType.SEA:
                            self.renderer.draw_circle(center + vector, 5, (0, 0, 255), 5)

            checkpoint_text = f"Checkpoint: {car.checkpoint_number}"
            distance_to_next_text = f"Distance to next: {car.distance_to_next_checkpoint}"
            angle_to_next_text = f"Angle to next: {car.angle_to_next_checkpoint}"
            position = car.car_entity.get_transform().get_position()
            forward = car.car_entity.get_transform().get_forward()
            entity_direction = f"Direction: {math.degrees(math.atan2(forward.y, forward.x))}"
            difference_between_forward_and_angle = abs(car.angle_to_next_checkpoint - math.degrees(math.atan2(forward.y, forward.x)))
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
            if car.selected_as_provisional_parent:
                self.renderer.draw_rect(car.car_entity.get_sprite_rect(), (0, 0, 255), 3)
                selected = True
                car.selected_as_provisional_parent = False
            elif car.selected_as_parent:
                car.selected_as_parent = False

        if selected:
            pygame.display.flip()
            # Wait 2 seconds
            time.sleep(2)

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
        car = self.cars[0]
        if len(self.cars) == 1:
            self.camera.set_position(car.car_entity.get_transform().get_position())
        else:
            for c in self.cars:
                if c.car_entity.get_fitness() > car.car_entity.get_fitness():
                    car = c
        car_position = car.car_entity.get_transform().get_position()
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
        num = 0
        for tile, npc in field_of_view:
            if tile is not None:
                if npc == 0:
                    self.renderer.draw_rect(tile.tile_entity.get_sprite_rect(), (255, 0, 0), 1)
                    self.renderer.draw_circle(tile.tile_entity.get_transform().get_position(), 2, (255, 255, 0), 1)
                elif npc == 1:
                    self.renderer.draw_rect(tile.tile_entity.get_sprite_rect(), (0, 0, 255), 1)
                if num < 10:
                    text_position = tile.tile_entity.get_transform().get_position()
                    text_position = text_position[0] + 4, text_position[1]
                else:
                    text_position = tile.tile_entity.get_transform().get_position()
                self.renderer.draw_provisional_text(str(num), text_position, (0, 0, 255), size=10)
            num += 1

    def _render_checkpoints(self):
        for tile in self.tile_map.checkpoints:
            self.renderer.draw_rect(tile.tile_entity.get_sprite_rect(), (255, 255, 0), 1)
            tile_position = tile.tile_entity.get_transform().get_position()
            if tile.checkpoint_number < 10:
                checkpoint_text_position = tile_position[0] + 4, tile_position[1]
            else:
                checkpoint_text_position = tile_position
            self.renderer.draw_text(str(tile.checkpoint_number), checkpoint_text_position, (255, 255, 0))

    def _change_input_manager_to_AI(self):
        if self.game_mode is GameMode.AI_TRAINING:
            self.input_manager = self.ai_manager.ai_input_manager
