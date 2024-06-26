import pygame
from pygame import Rect, Vector2

from engine.components.transform import Transform
from engine.managers.entity_manager.entity_manager import EntityManager
from engine.managers.input_manager.input_manager import InputManager
from engine.managers.render_manager.renderer import DebugRenderer, Renderer
from game.ai.ai_input_manager import AIInputManager
from game.ai.ai_manager import AIManager, population_size
from game.entities.NPC import NPC
from game.entities.car import Car
from game.game_mode import GameMode
from game.game_state.chronometer import Chronometer
from game.map.map_types import MapType
from game.map.tile_map import TileMap


class CarsManager:
    def __init__(self, game_mode: GameMode, tile_map: TileMap, entity_manager: EntityManager,
                 input_manager: InputManager, renderer: Renderer, debug_renderer: DebugRenderer,
                 chronometer: Chronometer = None):
        self.game_mode = game_mode
        self.renderer = renderer
        self.debug_renderer = debug_renderer
        self.tile_map = tile_map
        self.input_manager = input_manager
        self.entity_manager = entity_manager
        self.cars: [Car] = []
        self.chronometer = chronometer
        self.ai_manager: AIManager = AIManager(self.initialize, self.entity_manager,
                                               self.game_mode == GameMode.AI_TRAINING)

    def get_cars(self):
        return self.cars

    def create_car(self, is_training: bool) -> Car:
        entity: int = self.entity_manager.create_entity("entities/car", has_collider=True, is_static=False,
                                                        is_training=is_training)
        if self.game_mode == GameMode.MANUAL:
            return Car(entity, self.entity_manager, self.input_manager)
        return Car(entity, self.entity_manager, AIInputManager())

    def get_ai_manager(self):
        return self.ai_manager

    def initialize(self):
        if len(self.cars) == 0:
            if self.game_mode == GameMode.MANUAL or self.game_mode == GameMode.AI_PLAYING:
                self.cars.append(self.create_car(False))
            elif self.game_mode == GameMode.AI_TRAINING:
                for i in range(population_size):
                    self.cars.append(self.create_car(True))

        map_width = self.tile_map.width // 16
        tile_id = self.tile_map.tiles[(11 + 8) + (42 + 8) * map_width].entity_ID
        start_tile = self.entity_manager.get_transform(tile_id).get_position()

        for car in self.cars:
            # self.entity_manager.reset_entities()
            self.entity_manager.reset_entity(car.entity_ID)
            car.reset()
            self.entity_manager.get_transform(car.entity_ID).set_position(
                Vector2(start_tile[0], start_tile[1]))  # car.set_position(Vector2(start_tile[0], start_tile[1]))

    def update_cars(self, delta_time: float, npcs: list[NPC]):
        if self.game_mode is GameMode.AI_TRAINING or self.game_mode is GameMode.AI_PLAYING:
            self.ai_manager.update(self.cars, self.input_manager, self.chronometer)
        i: int
        car: Car
        for i, car in enumerate(self.cars):
            car_knowledge = car.car_knowledge
            fov = car_knowledge.field_of_view
            car_entity_id = car.entity_ID

            car_transform: Transform = self.entity_manager.get_transform(car_entity_id)
            npc_transforms: list[Transform] = [self.entity_manager.get_transform(npc.entity_ID) for npc in npcs]

            fov.update(car_transform, self.tile_map, npc_transforms)

            checkpoint = self.tile_map.get_checkpoint_in(fov.get_checkpoint_activation_area())

            car_in_tile = self.tile_map.get_tile_at(car_transform.get_position())

            total_checkpoints = len(self.tile_map.checkpoints)
            car_knowledge.reach_checkpoint(checkpoint, total_checkpoints)
            next_checkpoint_position = self.tile_map.get_next_checkpoint_position(car_knowledge.checkpoint_number)

            car_forward = car_transform.get_forward()
            car_velocity = self.entity_manager.get_physics(car_entity_id).get_velocity()

            collider = self.entity_manager.get_collider(car_entity_id)
            car_knowledge.update(car_in_tile.tile_type, next_checkpoint_position, car_forward, car_velocity, collider,
                                 car_transform.get_position(), self.chronometer)

            if checkpoint is not None:
                car.traveled_distance = checkpoint * 10

            car.update_input()
            car.update(delta_time)

    def render_car_knowledge(self):
        for car in self.cars:
            if self.game_mode == GameMode.AI_PLAYING or self.game_mode == GameMode.MANUAL:
                self._render_field_of_view(car)

                colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255),
                          (128, 0, 128), (128, 128, 0), (0, 128, 128), (128, 0, 0), (0, 128, 0), (0, 0, 128),
                          (128, 128, 128)]
                center = Vector2(200, 200)
                i = 0
                color = colors[0]
                for vector in self.tile_map.positions:
                    # cada 12, pasar al siguiente color
                    if i % 12 == 0:
                        color = colors[i // 12]
                    self.debug_renderer.draw_circle_absolute(center + vector, 5, color, 3)
                    self.renderer.draw_text_absolute(f"{i}", center + vector, (255, 255, 255), 10)
                    i += 1
                center = Vector2(200, 500)
                for tile, vector in zip(car.car_knowledge.field_of_view.get(), self.tile_map.positions):
                    if tile is not None:
                        if tile.tile_type == MapType.TRACK:
                            self.debug_renderer.draw_circle_absolute(center + vector, 5, (0, 0, 0), 5)
                        elif tile.tile_type == MapType.GRASS:
                            self.debug_renderer.draw_circle_absolute(center + vector, 5, (0, 255, 0), 5)
                        elif tile.tile_type == MapType.SIDEWALK:
                            self.debug_renderer.draw_circle_absolute(center + vector, 5, (155, 155, 155), 5)
                        elif tile.tile_type == MapType.SEA:
                            self.debug_renderer.draw_circle_absolute(center + vector, 5, (0, 0, 255), 5)

    def _render_field_of_view(self, car: Car):
        vision_box: list[pygame.Vector2] = car.car_knowledge.field_of_view.get_vision_box()
        self.debug_renderer.draw_polygon(vision_box, (255, 0, 0), 3)
        field_of_view = car.car_knowledge.field_of_view.get()
        tiles_with_entity = car.car_knowledge.field_of_view.get_tiles_with_entities_in_fov()
        num = 0
        for tile in field_of_view:
            if tile is not None:
                sprite_rect = self.entity_manager.get_sprite_rect(tile.entity_ID)
                transform = self.entity_manager.get_transform(tile.entity_ID)
                self.debug_renderer.draw_rect(sprite_rect, (255, 0, 0), 1)
                self.debug_renderer.draw_circle(transform.get_position().copy(), 2, (255, 255, 0), 1)

                if num < 10:
                    text_position = transform.get_position().copy()
                    text_position = Vector2(text_position[0] + 4, text_position[1])
                else:
                    text_position = transform.get_position().copy()
                self.renderer.draw_text(str(num), text_position, (0, 0, 255), size=10)
            num += 1

        for index in tiles_with_entity:
            tile = field_of_view[index]
            sprite_rect = self.entity_manager.get_sprite_rect(tile.entity_ID)
            self.debug_renderer.draw_rect(sprite_rect, (0, 0, 255), 2)
        vision_box: list[pygame.Vector2] = car.car_knowledge.field_of_view.entities_vision_box
        self.debug_renderer.draw_polygon(vision_box, (255, 0, 0), 3)
