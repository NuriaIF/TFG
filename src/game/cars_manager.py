"""
This module contains the CarsManager class
"""
import numpy as np
import pygame
from pygame import Vector2

from src.engine.components.collider import Collider
from src.engine.components.transform import Transform
from src.engine.managers.entity_manager.entity_manager import EntityManager
from src.engine.managers.render_manager.renderer import DebugRenderer, Renderer
from src.game.ai.ai_info.chronometer import Chronometer
from src.game.ai.ai_manager import AIManager
from src.game.entities.car import Car
from src.game.entities.tile import Tile
from src.game.map.map_types import MapType
from src.game.map.tile_map import TileMap


class CarsManager:
    """
    This class manages all the cars in the game
    It is responsible for creating, updating and rendering the cars
    Also it handles the AI knowledge and training
    """
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

    def set_number_of_cars(self, number_of_cars: int) -> None:
        """
        Set the number of cars to create
        :param number_of_cars: The number of cars
        :return: None
        """
        self._number_of_cars = number_of_cars

    def set_ai_manager(self, ai_manager: AIManager) -> None:
        """
        Set the AI manager that will handle the AI of the cars
        :param ai_manager: The AI manager
        :return: None
        """
        self._ai_manager = ai_manager

    def get_cars(self) -> list[Car]:
        """
        Get the list of car entities
        :return: The list of car entities
        """
        return self._cars

    def add_car(self, car: Car) -> None:
        """
        Add a car to the list of cars
        :param car: The car to add
        :return: None
        """
        self._cars.append(car)

    def create_car_entity(self) -> int:
        """
        Create a car entity
        Calls the entity manager to create a car entity
        :return:
        """
        entity: int = self._entity_manager.create_entity("entities/car", has_collider=True, is_static=False)
        self._entity_manager.get_physics(entity).set_mass(10000)  # Needed for collisions
        return entity

    def get_ai_manager(self) -> AIManager:
        """
        Get the AI manager of the cars
        :return: The AI manager
        """
        return self._ai_manager

    def initialize(self) -> None:
        """
        Initialize the car entities and the AI for each car
        :return: None
        """
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

    def handle_ai_knowledge(self, car: Car, tile_of_car: Tile) -> None:
        """
        This method updates the FOV of the car, the checkpoint reached and the car knowledge
        :param car: The car entity
        :param tile_of_car: The tile where the car is
        :return: None
        """
        car_knowledge = car.car_knowledge
        fov = car_knowledge.field_of_view
        car_entity_id = car.entity_ID

        car_transform: Transform = self._entity_manager.get_transform(car_entity_id)

        fov.update(car_transform, self._tile_map)

        checkpoint = self._tile_map.get_tile_at_pos_vec(car_transform.get_position()).checkpoint_number

        total_checkpoints = len(self._tile_map.checkpoints)
        car_knowledge.reach_checkpoint(checkpoint, total_checkpoints)
        next_checkpoint_position = self._tile_map.get_next_checkpoint_position(car_knowledge.checkpoint_number)

        car_velocity = self._entity_manager.get_physics(car_entity_id).get_velocity()

        collider = self._entity_manager.get_collider(car_entity_id)
        car_knowledge.update(tile_of_car.tile_type, next_checkpoint_position, car_velocity, collider,
                             car_transform.get_position(), self._chronometer, self.checkpoints_distances)

    def handle_ai_training(self, car: Car, tile_of_car: Tile):
        """
        This method handles the training of the AI
        This will check for states where the car should be disabled and update the AI knowledge
        also will update the physics of the car to disable it completely from moving or colliding
        :param car: The car entity
        :param tile_of_car: The tile where the car is
        :return: None
        """
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

    def handle_car_out_of_bounds(self, car: Car, tile_of_car: Tile):
        """
        This method handles the case where the car is out of bounds
        If the car is out of bounds, it will be placed in the last checkpoint
        :param car: The car entity
        :param tile_of_car: The tile where the car is
        :return: None
        """
        if tile_of_car is None or tile_of_car.tile_type == MapType.SEA:
            last_checkpoint = self._tile_map.checkpoints[car.car_knowledge.checkpoint_number]
            last_checkpoint_position = (self._entity_manager.get_transform(last_checkpoint.entity_ID)
                                        .get_position().copy())
            car.set_position(last_checkpoint_position)
            return last_checkpoint
        return tile_of_car

    def render_car_knowledge(self):
        """
        Render the knowledge of the cars for debugging purposes
        This will render the FOV of the cars and the tiles that the cars can see
        :return: None
        """
        for car in self._cars:
            self._render_field_of_view(car)

            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255),
                      (128, 0, 128), (128, 128, 0), (0, 128, 128), (128, 0, 0), (0, 128, 0), (0, 0, 128),
                      (128, 128, 128)]
            center = Vector2(200, 200)
            i = 0
            color = colors[0]
            for vector in self._tile_map.positions:
                # Every 12 tiles change color
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
        """
        Render the field of view of the car for debugging purposes
        This will render the vision box of the car in form of a square and the tiles that the car can see
        :param car: The car entity
        :return: None
        """
        vision_box: list[pygame.Vector2] = car.car_knowledge.field_of_view.get_vision_box()
        vision_box_array = np.array(vision_box, dtype=np.int32)
        self._debug_renderer.draw_polygon(vision_box_array, (255, 0, 0), 3)
        field_of_view = car.car_knowledge.field_of_view.get()
        # tiles_with_entity = car.car_knowledge.field_of_view.get_tiles_with_entities_in_fov()
        num = 0
        # field_of_view = field_of_view[:72]
        for tile in field_of_view:
            if tile is not None:
                sprite_rect = self._entity_manager.get_sprite_rect(tile.entity_ID)
                transform = self._entity_manager.get_transform(tile.entity_ID)
                self._debug_renderer.draw_rect(sprite_rect, (255, 0, 0))

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
        """
        Get the number of cars
        :return: The number of cars
        """
        return self._number_of_cars

    def clear(self):
        """
        Clear the cars manager
        :return: None
        """
        self._cars.clear()
        self._number_of_cars = 1
        self._ai_manager = None
