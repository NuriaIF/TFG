from __future__ import annotations

import math

from pygame import Vector2, Rect

from engine.components.transform import Transform
from game.entities.tile import Tile
from game.map.map_types import MapType
from game.map.tile_map import TileMap, TILE_SIZE


class FOV:
    def __init__(self):
        self.field_of_view: list[Tile] = []
        self.activation_area: list[Tile] = []
        self.vision_box: list[Vector2] = []
        self.tiles_with_entities_in_fov: list[int] = []

    def get(self) -> list[Tile] | None:
        return self.field_of_view

    def get_vision_box(self) -> list[Vector2]:
        return self.vision_box

    def get_checkpoint_activation_area(self) -> list[Tile]:
        return self.activation_area

    def get_tiles_with_entities_in_fov(self) -> list[int]:
        return self.tiles_with_entities_in_fov

    def update(self, car_transform: Transform, tile_map: TileMap,
               npc_transforms: list[Transform],
               npc_sprite_rects: list[Rect]) -> None:
        self.vision_box = self._get_vision_box(car_transform, radius=6)
        self.field_of_view = self._get_field_of_view(car_transform, tile_map)
        self.activation_area = self._get_checkpoint_activation_area(car_transform, tile_map)
        self.tiles_with_entities_in_fov = self._get_tiles_with_entity(npc_transforms, npc_sprite_rects, tile_map,
                                                                      car_transform)

    def _get_field_of_view(self, transform: Transform, tile_map: TileMap) -> list[Tile, bool]:
        position = transform.get_position()
        angle = transform.get_rotation()
        tiles_within_square = tile_map.get_tiles_within_square((position.x, position.y),
                                                               radius=6,
                                                               vision_box=self.vision_box,
                                                               angle=angle)
        return tiles_within_square

    def _get_checkpoint_activation_area(self, transform: Transform, tile_map: TileMap) -> list[Tile]:
        position = transform.get_position()
        angle = transform.get_rotation()
        tiles_within_square = tile_map.get_tiles_within_square((position.x, position.y),
                                                               radius=2,
                                                               vision_box=self.vision_box,
                                                               angle=angle)
        return [tile for tile in tiles_within_square if tile.tile_type == MapType.TRACK]

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
            if transform.get_position().distance_to(car_transform.get_position()) > 8 * TILE_SIZE:
                continue
            tiles_with_entity.extend(tile_map.get_tiles_of_rect(transform.get_position(), sprite_rect))
        for i, tile in enumerate(self.field_of_view):
            if tile in tiles_with_entity:
                tiles_with_entity_index.append(i)
        return tiles_with_entity_index

    def _get_vision_box(self, transform: Transform, radius: float = 6) -> list[Vector2]:
        angle = transform.get_rotation()
        # Calculamos el centro del Rect
        vision = transform.get_position()
        radius_pixels = radius * TILE_SIZE
        center = Vector2(vision.x, vision.y)

        # Calculamos las esquinas del Rect
        points = [
            Vector2(center.x + radius_pixels, center.y - radius_pixels),
            Vector2(center.x + radius_pixels, center.y + radius_pixels),
            Vector2(center.x - radius_pixels, center.y + radius_pixels),
            Vector2(center.x - radius_pixels, center.y - radius_pixels),
        ]
        # Rotamos cada punto alrededor del centro
        rotated_points: list[Vector2] = [self._rotate_point(point, center, angle) for point in points]
        # Dibujamos el Rect rotado
        return rotated_points

    def _rotate_point(self, point, center, angle) -> Vector2:
        angle_rad = math.radians(angle)
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)

        # Translate point back to origin
        translated_x = point.x - center.x
        translated_y = point.y - center.y

        # Rotate point
        rotated_x = translated_x * cos_angle - translated_y * sin_angle
        rotated_y = translated_x * sin_angle + translated_y * cos_angle

        # Translate point back to its original location
        new_x = rotated_x + center.x
        new_y = rotated_y + center.y

        return Vector2(new_x, new_y)

    def get_encoded_version(self) -> list[float]:
        if len(self.field_of_view) == 0:
            return [0] * 144
        to_add = 144 - len(self.field_of_view)
        encoded_fov = []
        for i, tile in enumerate(self.field_of_view):
            if i in self.tiles_with_entities_in_fov:
                encoded_fov.append(-2.0)
            elif tile.tile_type == MapType.GRASS:
                encoded_fov.append(-0.75)
            elif tile.tile_type == MapType.SIDEWALK:
                encoded_fov.append(-0.5)
            elif tile.tile_type == MapType.TRACK:
                encoded_fov.append(1.0)
            elif tile.tile_type == MapType.SEA:
                encoded_fov.append(-2.0)
            else:
                encoded_fov.append(-1.0)
        for _ in range(to_add):
            encoded_fov.append(-1.0)
        return encoded_fov
