import pygame
from pygame import Vector2

from engine.components.collider import Collider
from engine.components.transform import Transform
from engine.managers.entity_manager.entity_manager import EntityManager
from engine.managers.input_manager.input_manager import InputManager
from engine.managers.render_manager.renderer import DebugRenderer, Renderer
from game.AI.AI_input_manager import AIInputManager
from game.AI.AI_manager import AIManager, population_size
from game.entities.NPC import NPC
from game.entities.car import Car
from game.entities.tile import Tile
from game.game_mode import GameMode
from game.game_state.chronometer import Chronometer
from game.map.map_types import MapType
from game.map.tile_map import TileMap, TILE_SIZE


class CarsManager:
    def __init__(self, game_mode: GameMode, tile_map: TileMap, entity_manager: EntityManager,
                 input_manager: InputManager, renderer: Renderer, debug_renderer: DebugRenderer,
                 chronometer: Chronometer = None):
        self._game_mode = game_mode
        self._renderer = renderer
        self._debug_renderer = debug_renderer
        self._tile_map = tile_map
        self._input_manager = input_manager
        self._entity_manager = entity_manager
        self._cars: [Car] = []
        self._chronometer = chronometer
        self._ai_manager: AIManager = AIManager(self._entity_manager,
                                                self._game_mode == GameMode.AI_TRAINING)

        self._number_of_cars = 1
        if self._game_mode == GameMode.AI_TRAINING:
            self._number_of_cars = population_size
        self._npc_transforms: list[Transform] = []
        self._npc_sprite_rects: list[pygame.Rect] = []

        map_width = self._tile_map.width // 16
        self._initial_car_position = (11 + 8) + (42 + 8) * map_width
        # self._initial_car_position = Vector2((11 + 8) * TILE_SIZE, (42 + 8) * TILE_SIZE)

    def get_cars(self) -> list[Car]:
        return self._cars

    def create_car(self) -> Car:
        entity: int = self._entity_manager.create_entity("entities/car", has_collider=True, is_static=False)
        self._entity_manager.get_physics(entity).set_mass(10000)  # Needed for collisions
        if self._game_mode == GameMode.MANUAL:
            return Car(entity, self._entity_manager, self._input_manager)
        return Car(entity, self._entity_manager, AIInputManager())

    def get_ai_manager(self):
        return self._ai_manager

    def initialize(self):
        if len(self._cars) == 0:
            for i in range(self._number_of_cars):
                self._cars.append(self.create_car())

        tile_id = self._tile_map.tiles[self._initial_car_position].entity_ID
        start_tile = self._entity_manager.get_transform(tile_id).get_position()
        car: Car
        print("NEW INITIALIZATION")
        for car in self._cars:
            car.reset()
            self._entity_manager.get_transform(car.entity_ID).debug_config_show_transform()
            first_checkpoint_position = self._tile_map.get_next_checkpoint_position(0)
            car.car_knowledge.initialize(first_checkpoint_position)
            car.set_position(Vector2(start_tile[0], start_tile[1]))
            car_collider: Collider = self._entity_manager.get_collider(car.entity_ID)
            car_physics = self._entity_manager.get_physics(car.entity_ID)
            car_collider.set_active(True)
            car_physics.set_static(False)
            # Add all the cars to non-collideable colliders
            # So while its training, they don't collide with each other
            if self._game_mode is GameMode.AI_TRAINING:
                for other_car in self._cars:
                    other_car_collider: Collider = self._entity_manager.get_collider(other_car.entity_ID)
                    if car_collider is not other_car_collider:
                        car_collider.add_non_collideable_collider(other_car_collider)

    def update_cars(self, delta_time: float, npcs: list[NPC]):
        if self._game_mode is GameMode.AI_TRAINING or self._game_mode is GameMode.AI_PLAYING:
            self._ai_manager.update(self._cars, self._input_manager, self._chronometer)
        i: int
        car: Car
        for i, car in enumerate(self._cars):
            car_transform: Transform = self._entity_manager.get_transform(car.entity_ID)
            tile_of_car: Tile = self._tile_map.get_tile_at_pos(car_transform.get_position())

            self.handle_ai_knowledge(car, tile_of_car, npcs)

            if GameMode.AI_TRAINING:
                self.handle_ai_training(car, tile_of_car)

            car.update_input()
            car.update(delta_time)

    def handle_ai_knowledge(self, car: Car, tile_of_car: Tile, npcs: list[NPC]):
        car_knowledge = car.car_knowledge
        fov = car_knowledge.field_of_view
        car_entity_id = car.entity_ID

        car_transform: Transform = self._entity_manager.get_transform(car_entity_id)
        if len(self._npc_transforms) == 0:
            self._npc_transforms = [self._entity_manager.get_transform(npc.entity_ID) for npc in npcs]
            self._npc_sprite_rects = [self._entity_manager.get_sprite_rect(npc.entity_ID) for npc in npcs]

        fov.update(car_transform, self._tile_map, self._npc_transforms, self._npc_sprite_rects)

        checkpoint = self._tile_map.get_checkpoint_in(fov.get_checkpoint_activation_area())

        total_checkpoints = len(self._tile_map.checkpoints)
        car_knowledge.reach_checkpoint(checkpoint, total_checkpoints)
        next_checkpoint_position = self._tile_map.get_next_checkpoint_position(car_knowledge.checkpoint_number)

        car_forward = car_transform.get_forward()
        car_velocity = self._entity_manager.get_physics(car_entity_id).get_velocity()

        collider = self._entity_manager.get_collider(car_entity_id)
        car_knowledge.update(tile_of_car.tile_type, next_checkpoint_position, car_forward, car_velocity, collider,
                             car_transform.get_position(), self._chronometer)

        if checkpoint is not None:
            car.traveled_distance = checkpoint * 10

    def handle_ai_training(self, car: Car, tile_of_car: Tile):
        car_entity_id = car.entity_ID
        car_physics = self._entity_manager.get_physics(car_entity_id)
        car_collider = self._entity_manager.get_collider(car_entity_id)
        if car_collider.is_colliding() or tile_of_car.tile_type == MapType.SIDEWALK:
            car_physics.set_velocity(0)
            car_physics.set_acceleration(0)
            car_physics.set_force(0)
            car.car_knowledge.has_collided = True
            car_collider.set_active(False)
            self._entity_manager.get_physics(car_entity_id).set_vector_velocity(Vector2(0, 0))

    def render_debug(self):
        for car in self._cars:
            if car.selected_as_parent:
                sprite_rect = self._entity_manager.get_sprite_rect(car.entity_ID)
                self._debug_renderer.draw_rect(sprite_rect, (0, 0, 255), 3)
                car.selected_as_parent = False
            car_position = self._entity_manager.get_transform(car.entity_ID).get_position().copy()
            self._debug_renderer.draw_text_absolute(f"Checkpoint number: {car.car_knowledge.checkpoint_number}", Vector2(100, 0), (255, 255, 255))
        if len(self._ai_manager.get_agents()) > 0:
            sorted_list = sorted(self._ai_manager.get_agents(), key=lambda x: x.fitness_score, reverse=True)
            agent_with_best_fitness = sorted_list[0]
            self._debug_renderer.draw_rect_absolute(
                self._entity_manager.get_sprite_rect(agent_with_best_fitness.controlled_entity.entity_ID), (0, 255, 0),
                3)

    def render_car_knowledge(self):
        for car in self._cars:
            if self._game_mode == GameMode.AI_PLAYING or self._game_mode == GameMode.MANUAL:
                self._render_field_of_view(car)

                colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255),
                          (128, 0, 128), (128, 128, 0), (0, 128, 128), (128, 0, 0), (0, 128, 0), (0, 0, 128),
                          (128, 128, 128)]
                center = Vector2(200, 200)
                i = 0
                color = colors[0]
                for vector in self._tile_map.positions:
                    # cada 12, pasar al siguiente color
                    if i % 12 == 0:
                        color = colors[i // 12]
                    self._debug_renderer.draw_circle_absolute(center + vector, 5, color, 3)
                    self._renderer.draw_text_absolute(f"{i}", center + vector, (255, 255, 255), 10)
                    i += 1
                center = Vector2(200, 500)
                for tile, vector in zip(car.car_knowledge.field_of_view.get(), self._tile_map.positions):
                    if tile is not None:
                        if tile.tile_type == MapType.TRACK:
                            self._debug_renderer.draw_circle_absolute(center + vector, 5, (0, 0, 0), 5)
                        elif tile.tile_type == MapType.GRASS:
                            self._debug_renderer.draw_circle_absolute(center + vector, 5, (0, 255, 0), 5)
                        elif tile.tile_type == MapType.SIDEWALK:
                            self._debug_renderer.draw_circle_absolute(center + vector, 5, (155, 155, 155), 5)
                        elif tile.tile_type == MapType.SEA:
                            self._debug_renderer.draw_circle_absolute(center + vector, 5, (0, 0, 255), 5)

    def _render_field_of_view(self, car: Car):
        vision_box: list[pygame.Vector2] = car.car_knowledge.field_of_view.get_vision_box()
        self._debug_renderer.draw_polygon(vision_box, (255, 0, 0), 3)
        field_of_view = car.car_knowledge.field_of_view.get()
        tiles_with_entity = car.car_knowledge.field_of_view.get_tiles_with_entities_in_fov()
        num = 0
        for tile in field_of_view:
            if tile is not None:
                sprite_rect = self._entity_manager.get_sprite_rect(tile.entity_ID)
                transform = self._entity_manager.get_transform(tile.entity_ID)
                self._debug_renderer.draw_rect(sprite_rect, (255, 0, 0), 1)

                # if num < 10:
                #     text_position = transform.get_position().copy()
                #     text_position = Vector2(text_position[0] + 4, text_position[1])
                # else:
                #     text_position = transform.get_position().copy()
                # self._renderer.draw_text(str(num), text_position, (0, 0, 255), size=10)
            num += 1

        for index in tiles_with_entity:
            tile = field_of_view[index]
            sprite_rect = self._entity_manager.get_sprite_rect(tile.entity_ID)
            self._debug_renderer.draw_rect(sprite_rect, (0, 0, 255), 2)
