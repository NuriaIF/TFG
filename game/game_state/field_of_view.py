from __future__ import annotations

from engine.entities.entity import Entity
from game.entities.tile import Tile
from game.map.map_types import MapType
from game.map.tile_map import TileMap


class FOV:
    def __init__(self):
        self.field_of_view: list[[Tile | None] | bool] = None
        self.nearest_tile = None

    def get(self) -> list[[Tile | None], bool] | None:
        return self.field_of_view

    def get_tiles_in_FOV(self) -> list[Tile]:
        return [tile for tile, _ in self.field_of_view if tile is not None]

    def get_nearest_tile(self) -> Tile | None:
        return self.nearest_tile

    def update(self, entity: Entity, tile_map: TileMap, entities: list[Entity]) -> None:
        self.field_of_view = self._get_field_of_view(entity, tile_map, entities)

    def _get_field_of_view(self, entity: Entity, tile_map: TileMap, entities: list[Entity]) -> list[[Tile | None], bool]:
        tiles_within_square_and_center = tile_map.get_tiles_within_square((entity.get_transform().get_position().x,
                                                                           entity.get_transform().get_position().y),
                                                                          self.nearest_tile,
                                                                          radius=6)
        tiles_within_square = tiles_within_square_and_center[0]
        self.nearest_tile = tiles_within_square_and_center[1]
        tiles_and_entities_within_square = self._get_tiles_with_entity(tiles_within_square, entities)
        return tiles_and_entities_within_square

    def _get_tiles_with_entity(self, tiles_within_square: list[Tile | None], entities: list[Entity]) \
            -> list[[Tile | None], bool]:
        tiles_and_entities_within_square: list[[Tile | None], bool] = []
        for tile in tiles_within_square:
            if tile is None:
                tiles_and_entities_within_square.append([None, 0])
            else:
                has_entity = False
                for entity in entities:
                    if entity.get_sprite_rect().colliderect(tile.tile_entity.get_sprite_rect()):
                        tiles_and_entities_within_square.append([tile, 1])
                        has_entity = True
                if not has_entity:
                    tiles_and_entities_within_square.append([tile, 0])

        return tiles_and_entities_within_square

    def get_encoded_version(self) -> list[float]:
        encoded_fov = []
        for tile, has_entity in self.field_of_view:
            if tile is None:
                encoded_fov.append(-1)
            elif tile.tile_type == MapType.GRASS:
                encoded_fov.append(-0.75)
            elif tile.tile_type == MapType.SIDEWALK:
                encoded_fov.append(-0.5)
            elif tile.tile_type == MapType.TRACK:
                encoded_fov.append(1)
            else:
                encoded_fov.append(-1)
            if has_entity:
                encoded_fov.append(1)
            else:
                encoded_fov.append(0)
        return encoded_fov
