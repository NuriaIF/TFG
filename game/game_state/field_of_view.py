from __future__ import annotations

import numpy as np
from pygame import Vector2, Rect

from engine.components.transform import Transform
from engine.managers.entity_manager.entity_manager import EntityManager
from game.entities.tile import Tile
from game.map.map_types import MapType
from game.map.tile_map import TileMap, TILE_SIZE


class FOV:
    def __init__(self):
        self.field_of_view: list[tuple[Tile, bool]] = []
        self.nearest_tile = None
        self.activation_area: list[Tile] = []
        self.vision_box: list[Vector2] = []

    def get(self) -> list[tuple[Tile, bool]] | None:
        return self.field_of_view

    def get_vision_box(self) -> list[Vector2]:
        return self.vision_box

    def get_checkpoint_activation_area(self) -> list[Tile]:
        return self.activation_area

    def get_nearest_tile(self) -> Tile:
        return self.nearest_tile

    def update(self, transform: Transform, tile_map: TileMap, sprite_rects: list[Rect], entity_manager: EntityManager
               ) -> None:
        angle: [] = np.degrees(np.arctan2(transform.get_forward().y,
                                          transform.get_forward().x))
        self.vision_box = self._get_vision_box(transform, radius=6, angle=angle)
        self.field_of_view = self._get_field_of_view(transform, tile_map, sprite_rects, angle=angle,
                                                     entity_manager=entity_manager)
        self.activation_area = self._get_checkpoint_activation_area(transform, tile_map, angle=angle)

    def _get_field_of_view(self, transform: Transform, tile_map: TileMap, sprite_rects: list[Rect], angle: [],
                           entity_manager: EntityManager) -> list[tuple[Tile, bool]]:
        tiles_within_square_and_center = tile_map.get_tiles_within_square((transform.get_position().x,
                                                                           transform.get_position().y),
                                                                          self.nearest_tile,
                                                                          radius=6,
                                                                          vision_box=self.vision_box,
                                                                          angle=angle)
        tiles_within_square = tiles_within_square_and_center[0]
        self.nearest_tile = tiles_within_square_and_center[1]
        tiles_and_entities_within_square = self._get_tiles_with_entity(tiles_within_square, sprite_rects, entity_manager)
        return tiles_and_entities_within_square

    def _get_checkpoint_activation_area(self, transform: Transform, tile_map: TileMap, angle: []) -> list[Tile]:
        tiles_within_square_and_center = tile_map.get_tiles_within_square((transform.get_position().x,
                                                                           transform.get_position().y),
                                                                          self.nearest_tile,
                                                                          radius=3,
                                                                          vision_box=self.vision_box,
                                                                          angle=angle)
        tiles_within_square = tiles_within_square_and_center[0]
        return [tile for tile in tiles_within_square if tile is not None and tile.tile_type == MapType.TRACK]

    def _get_tiles_with_entity(self, tiles_within_square: list[Tile], sprite_rects: list[Rect],
                               entity_manager: EntityManager) -> list[tuple[Tile, bool]]:
        tiles_and_entities_within_square: list[tuple[Tile, bool]] = []
        for tile in tiles_within_square:
            tile_sprite_rect = entity_manager.get_sprite_rect(tile.entity_ID)
            if tile is not None:
                has_entity = False
                for sprite_rect in sprite_rects:
                    if sprite_rect.colliderect(tile_sprite_rect):
                        tiles_and_entities_within_square.append((tile, True))
                        has_entity = True
                if not has_entity:
                    tiles_and_entities_within_square.append((tile, False))

        return tiles_and_entities_within_square

    def _get_vision_box(self, transform: Transform, angle: [], radius=6):
        # Calculamos el centro del Rect
        vision = transform.get_position()
        radius_pixels = radius * TILE_SIZE
        vision_rect = Rect(vision.x - radius_pixels, vision.y - radius_pixels, 2 * radius_pixels, 2 * radius_pixels)
        center = Vector2([vision_rect.centerx, vision_rect.centery])

        # Calculamos las esquinas del Rect
        points = [
            Vector2([vision_rect.topright[0], vision_rect.topright[1]]),
            Vector2([vision_rect.bottomright[0], vision_rect.bottomright[1]]),
            Vector2([vision_rect.bottomleft[0], vision_rect.bottomleft[1]]),
            Vector2([vision_rect.topleft[0], vision_rect.topleft[1]]),
        ]
        # Rotamos cada punto alrededor del centro
        rotated_points: list[Vector2] = [self._rotate_point(point, center, angle) for point in points]
        # Dibujamos el Rect rotado
        return rotated_points

    def _rotate_point(self, point, center, angle) -> Vector2:
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

    def get_encoded_version(self) -> list[float]:
        if len(self.field_of_view) == 0:
            return [0] * 288
        to_add = 144 - len(self.field_of_view)
        encoded_fov = []
        for tile, has_entity in self.field_of_view:
            if tile.tile_type == MapType.GRASS:
                encoded_fov.append(-0.75)
            elif tile.tile_type == MapType.SIDEWALK:
                encoded_fov.append(-0.5)
            elif tile.tile_type == MapType.TRACK:
                encoded_fov.append(1.0)
            else:
                encoded_fov.append(-1.0)
            if has_entity:
                encoded_fov.append(1.0)
            else:
                encoded_fov.append(0.0)
        for _ in range(to_add):
            encoded_fov.append(-1.0)
            encoded_fov.append(0.0)
        return encoded_fov
