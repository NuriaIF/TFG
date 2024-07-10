"""
This module contains the class FOV that represents the field of view of the car in the game.
"""
from typing import Optional

import numpy as np
from numpy import ndarray
from pygame import Rect

from src.engine.components.transform import Transform
from src.engine.math.geometry import calculate_polygon
from src.game.entities.tile import Tile
from src.game.map.tile_map import TileMap, TILE_SIZE

forward_array = np.zeros(2, dtype=np.float64)
position_array = np.zeros(2, dtype=np.float64)


class FOV:
    """
    Class that represents the field of view of the car in the game.
    The purpose of this class is to calculate all the tiles that are in the field of view of the car.
    """
    def __init__(self):
        self.field_of_view: list[Tile] = []
        self.vision_box: ndarray = np.zeros((4, 2), dtype=np.float64)
        self.tiles_with_entities_in_fov: list[int] = []
        self.field_of_view_encoded: list[float] = []

    def get(self) -> Optional[list[Tile]]:
        """
        Get the field of view of the car as a list of tiles.
        :return: The field of view of the car
        """
        return self.field_of_view

    def get_vision_box(self) -> ndarray:
        """
        Get the vision box of the car.
        :return: The vision box of the car
        """
        return self.vision_box

    def get_tiles_with_entities_in_fov(self) -> list[int]:
        """
        Get the tiles with entities in the field of view of the car.
        This only works if there are other entities in the game.
        :return: The tiles with entities in the field of view of the car
        """
        return self.tiles_with_entities_in_fov

    def update(self, car_transform: Transform, tile_map: TileMap) -> None:
        """
        Update the field of view of the car.
        This will call calculate_polygon to obtain a polygon (rotated square) and then get the tiles within that square.
        :param car_transform: The transform of the car
        :param tile_map: The tile map of the game
        :return: None
        """
        forward = car_transform.get_forward()
        position = car_transform.get_position()
        angle = car_transform.get_rotation()
        forward_array[0] = forward.x
        forward_array[1] = forward.y
        position_array[0] = position.x
        position_array[1] = position.y
        self.vision_box: ndarray = calculate_polygon(angle, forward_array, position_array, TILE_SIZE, radius=6)
        self.field_of_view = self._get_field_of_view(car_transform, tile_map)

    def _get_field_of_view(self, transform: Transform, tile_map: TileMap) -> list[Tile, bool]:
        """
        Get the field of view of the car as a list of tiles.
        This method is called by update to get the field of view of the car to update the attribute field_of_view.
        :param transform:
        :param tile_map:
        :return:
        """
        position = transform.get_position()
        angle = transform.get_rotation()
        forward = transform.get_forward()
        # Sum 6 tiles in the forward direction
        pos = position.x + forward.x * 6 * TILE_SIZE, position.y + forward.y * 6 * TILE_SIZE
        tiles_within_square_and_codes = tile_map.get_tiles_within_square((pos[0], pos[1]),
                                                                         radius=6,
                                                                         vision_box=self.vision_box,
                                                                         angle=angle)
        tiles_within_square = tiles_within_square_and_codes[0]
        self.field_of_view_encoded = tiles_within_square_and_codes[1]
        return tiles_within_square

    def _get_tiles_with_entity(self,
                               npc_transforms: list[Transform],
                               npc_sprite_rects: list[Rect],
                               tile_map: TileMap,
                               car_transform: Transform) -> list[int]:
        """
        Get the tiles with entities in the field of view of the car.
        This only works and is useful if there are other entities in the game.
        :param npc_transforms: All the transforms of the NPCs
        :param npc_sprite_rects: All the sprite rects of the NPCs
        :param tile_map: The tile map of the game
        :param car_transform: The transform of the car
        :return: The tiles with entities in the field of view of the car
        """
        tiles_with_entity: list[Tile] = []
        tiles_with_entity_index: list[int] = []
        transform: Transform
        sprite_rect: Rect
        for transform, sprite_rect in zip(npc_transforms, npc_sprite_rects):
            if transform.get_position().distance_to(car_transform.get_position()) > 12 * TILE_SIZE:
                continue
            tiles_with_entity.extend(tile_map.get_tiles_of_rect(transform.get_position(), sprite_rect))
        for i, tile in enumerate(self.field_of_view):
            if tile in tiles_with_entity:
                tiles_with_entity_index.append(i)
        return tiles_with_entity_index

    def get_encoded_version(self) -> list[float]:
        """
        This returns a list of 144 elements that represents the field of view of the car in an encoded version.
        The purpose of this method is to be used as input for the neural network.
        :return: The encoded version of the field of view as a list of 144 floats
        """
        if len(self.field_of_view_encoded) == 0:
            return [0] * 144
        to_add = 144 - len(self.field_of_view_encoded)

        for _ in range(to_add):
            self.field_of_view_encoded.append(-1.0)
        return self.field_of_view_encoded
