import pygame
from pygame import Vector2

from src.engine.components.collider import Collider
from src.engine.components.transform import Transform
from src.engine.managers.entity_manager.entity_manager import EntityManager
from src.engine.managers.render_manager.renderer import DebugRenderer, Renderer
from src.game.AI.AI_manager import AIManager
from src.game.AI.ai_info.chronometer import Chronometer
from src.game.entities.car import Car
from src.game.entities.tile import Tile
from src.game.map.map_types import MapType
from src.game.map.tile_map import TileMap


class CarsManager:
    def __init__(self, tile_map: TileMap, entity_manager: EntityManager, renderer: Renderer,
                 debug_renderer: DebugRenderer,
                 checkpoints_distances: list[float],
                 chronometer: Chronometer = None):
        self._ai_manager = None
        self._renderer = renderer
        self._debug_renderer = debug_renderer
        self._tile_map = tile_map
        self._entity_manager = entity_manager
        self._cars: [Car] = []
        self._chronometer = chronometer
        self._generation_chronometer = Chronometer()

        self.checkpoints_distances = checkpoints_distances

        self._number_of_cars = 1

        map_width = self._tile_map.width // 16
        self._initial_car_position = (11 + 8) + (42 + 8) * map_width
        # self._initial_car_position = Vector2((11 + 8) * TILE_SIZE, (42 + 8) * TILE_SIZE)
        # self._ai_manager = AIManager(entity_manager, training=False)

    def set_number_of_cars(self, number_of_cars: int):
        self._number_of_cars = number_of_cars

    def set_ai_manager(self, ai_manager: AIManager):
        self._ai_manager = ai_manager

    def get_cars(self) -> list[Car]:
        return self._cars

    def add_car(self, car: Car):
        self._cars.append(car)

    def create_car_entity(self) -> int:
        entity: int = self._entity_manager.create_entity("entities/car", has_collider=True, is_static=False)
        self._entity_manager.get_physics(entity).set_mass(10000)  # Needed for collisions
        return entity

    def get_ai_manager(self):
        return self._ai_manager

    def initialize(self):
        self._generation_chronometer.reset()
        self._generation_chronometer.start()
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
            for other_car in self._cars:
                other_car_collider: Collider = self._entity_manager.get_collider(other_car.entity_ID)
                if car_collider is not other_car_collider:
                    car_collider.add_non_collideable_collider(other_car_collider)

    def handle_ai_knowledge(self, car: Car, tile_of_car: Tile):
        car_knowledge = car.car_knowledge
        fov = car_knowledge.field_of_view
        car_entity_id = car.entity_ID

        car_transform: Transform = self._entity_manager.get_transform(car_entity_id)

        fov.update(car_transform, self._tile_map)

        checkpoint = self._tile_map.get_tile_at_pos_vec(car_transform.get_position()).checkpoint_number

        total_checkpoints = len(self._tile_map.checkpoints)
        car_knowledge.reach_checkpoint(checkpoint, total_checkpoints)
        next_checkpoint_position = self._tile_map.get_next_checkpoint_position(car_knowledge.checkpoint_number)

        car_forward = car_transform.get_forward()
        car_velocity = self._entity_manager.get_physics(car_entity_id).get_velocity()

        collider = self._entity_manager.get_collider(car_entity_id)
        car_knowledge.update(tile_of_car.tile_type, next_checkpoint_position, car_forward, car_velocity, collider,
                             car_transform.get_position(), self._chronometer, self.checkpoints_distances)

    def handle_ai_training(self, car: Car, tile_of_car: Tile):
        car_entity_id = car.entity_ID
        car_physics = self._entity_manager.get_physics(car_entity_id)
        car_collider = self._entity_manager.get_collider(car_entity_id)
        if car_collider.is_colliding() or tile_of_car.tile_type == MapType.SIDEWALK\
                or (self._generation_chronometer.get_elapsed_time() > 1 and abs(car_physics.get_velocity()) < 7):
            car.disable()
            car_physics.set_velocity(0)
            car_physics.set_acceleration(0)
            car_physics.set_force(0)
            car.car_knowledge.has_collided = True
            car_collider.set_active(False)
            self._entity_manager.get_physics(car_entity_id).set_vector_velocity(Vector2(0, 0))

    def render_car_knowledge(self):
        for car in self._cars:
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
                pos = Vector2(center[0] + vector[0], center[1] - vector[1])
                self._debug_renderer.draw_circle_absolute(pos, 5, color, 3)
                self._renderer.draw_text_absolute(f"{i}", pos, (255, 255, 255), 10)
                i += 1
            center = Vector2(200, 500)
            for tile, vector in zip(car.car_knowledge.field_of_view.get(), self._tile_map.positions):
                if tile is not None:
                    pos = Vector2(center[0] + vector[0], center[1] - vector[1])
                    if tile.tile_type == MapType.TRACK:
                        self._debug_renderer.draw_circle_absolute(pos, 5, (0, 0, 0), 5)
                    elif tile.tile_type == MapType.GRASS:
                        self._debug_renderer.draw_circle_absolute(pos, 5, (0, 255, 0), 5)
                    elif tile.tile_type == MapType.SIDEWALK:
                        self._debug_renderer.draw_circle_absolute(pos, 5, (155, 155, 155), 5)
                    elif tile.tile_type == MapType.SEA:
                        self._debug_renderer.draw_circle_absolute(pos, 5, (0, 0, 255), 5)

    def _render_field_of_view(self, car: Car):
        vision_box: list[pygame.Vector2] = car.car_knowledge.field_of_view.get_vision_box()
        self._debug_renderer.draw_polygon(vision_box, (255, 0, 0), 3)
        field_of_view = car.car_knowledge.field_of_view.get()
        # tiles_with_entity = car.car_knowledge.field_of_view.get_tiles_with_entities_in_fov()
        num = 0
        # field_of_view = field_of_view[:72]
        for tile in field_of_view:
            if tile is not None:
                sprite_rect = self._entity_manager.get_sprite_rect(tile.entity_ID)
                transform = self._entity_manager.get_transform(tile.entity_ID)
                self._debug_renderer.draw_rect(sprite_rect, (255, 0, 0), 1)

                if num < 10:
                    position = transform.get_position()
                    text_position = Vector2(position[0] + 4, position[1])
                else:
                    text_position = transform.get_position()
                self._renderer.draw_text(str(num), text_position, (0, 0, 255), size=10)
            num += 1
        #
        # for index in tiles_with_entity:
        #     # if index > 71:
        #     #     continue
        #     tile = field_of_view[index]
        #     sprite_rect = self._entity_manager.get_sprite_rect(tile.entity_ID)
        #     self._debug_renderer.draw_rect(sprite_rect, (0, 0, 255), 2)

    def get_number_of_cars(self):
        return self._number_of_cars

    def clear(self):
        self._cars.clear()
        self._number_of_cars = 1
        self._ai_manager = None
