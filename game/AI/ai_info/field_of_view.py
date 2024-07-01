from __future__ import annotations

import numpy as np
from numba import njit, float64, uint32
from numpy import ndarray
from pygame import Vector2, Rect

from engine.components.transform import Transform
from game.entities.tile import Tile
from game.map.map_types import MapType
from game.map.tile_map import TileMap, TILE_SIZE

forward_array = np.zeros(2, dtype=np.float64)
position_array = np.zeros(2, dtype=np.float64)


@njit(float64[:](float64, float64, float64, float64, float64))
def rotate_point(x, y, center_x, center_y, angle):
    angle_rad = np.radians(angle)
    cos_angle = np.cos(angle_rad)
    sin_angle = np.sin(angle_rad)

    # Translate point back to origin
    translated_x = x - center_x
    translated_y = y - center_y

    # Rotate point
    rotated_x = translated_x * cos_angle - translated_y * sin_angle
    rotated_y = translated_x * sin_angle + translated_y * cos_angle

    # Translate point back to its original location
    new_x = rotated_x + center_x
    new_y = rotated_y + center_y

    return np.array([new_x, new_y])


@njit(float64[:, :](float64, float64[:], float64[:], float64, uint32))
def calculate_vision_box(angle: float, forward: ndarray, position: ndarray, tile_size: int,
                         radius: float = 6) -> ndarray:
    center = np.zeros(2, dtype=np.float64)
    points = np.zeros((4, 2), dtype=np.float64)
    rotated_points = np.zeros((4, 2), dtype=np.float64)
    # desplazar la posición 6 en dirección del forward
    center[0] = position[0] + forward[0] * radius * tile_size
    center[1] = position[1] + forward[1] * radius * tile_size
    radius_pixels = radius * tile_size

    # Calculamos las esquinas del Polygon
    points[0, 0] = center[0] + radius_pixels
    points[0, 1] = center[1] - radius_pixels
    points[1, 0] = center[0] + radius_pixels
    points[1, 1] = center[1] + radius_pixels
    points[2, 0] = center[0] - radius_pixels
    points[2, 1] = center[1] + radius_pixels
    points[3, 0] = center[0] - radius_pixels
    points[3, 1] = center[1] - radius_pixels

    # Rotamos cada punto alrededor del centro
    for i in range(4):
        rotated_points[i] = rotate_point(points[i, 0], points[i, 1], center[0], center[1], angle)
    # Dibujamos el Rect rotado
    return rotated_points


class FOV:
    def __init__(self):
        self.field_of_view: list[Tile] = []
        self.vision_box: ndarray = np.zeros((4, 2), dtype=np.float64)
        self.tiles_with_entities_in_fov: list[int] = []
        self.field_of_view_encoded: list[float] = []

    def get(self) -> list[Tile] | None:
        return self.field_of_view

    def get_vision_box(self) -> ndarray:
        return self.vision_box

    def get_tiles_with_entities_in_fov(self) -> list[int]:
        return self.tiles_with_entities_in_fov

    def update(self, car_transform: Transform, tile_map: TileMap,
               npc_transforms: list[Transform],
               npc_sprite_rects: list[Rect]) -> None:
        forward = car_transform.get_forward()
        position = car_transform.get_position()
        angle = car_transform.get_rotation()
        forward_array[0] = forward.x
        forward_array[1] = forward.y
        position_array[0] = position.x
        position_array[1] = position.y
        self.vision_box: ndarray = calculate_vision_box(angle, forward_array, position_array, TILE_SIZE, radius=6)
        self.field_of_view = self._get_field_of_view(car_transform, tile_map)
        # self.tiles_with_entities_in_fov = self._get_tiles_with_entity(npc_transforms, npc_sprite_rects, tile_map,
        #                                                               car_transform)

    def _get_field_of_view(self, transform: Transform, tile_map: TileMap) -> list[Tile, bool]:
        position = transform.get_position()
        angle = transform.get_rotation()
        forward = transform.get_forward()
        # sumar a la posición 6 en direccion del forward
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
        if len(self.field_of_view_encoded) == 0:
            return [0] * 144
        to_add = 144 - len(self.field_of_view_encoded)

        for _ in range(to_add):
            self.field_of_view_encoded.append(-1.0)
        return self.field_of_view_encoded
