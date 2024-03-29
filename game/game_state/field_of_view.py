from __future__ import annotations

from engine.entities.entity import Entity
from game.entities.tile import Tile
from game.map.tile_map import TileMap


class FOV:
    def __init__(self):
        self.field_of_view = None

    def get(self):
        return self.field_of_view

    def update(self, entity: Entity, tile_map: TileMap, entities: list[Entity]):
        self.field_of_view = self._get_field_of_view(entity, tile_map, entities)

    def _get_field_of_view(self, entity: Entity, tile_map: TileMap, entities: list[Entity]):
        tiles_within_square = tile_map.get_tiles_within_square((entity.get_transform().get_position().x,
                                                                entity.get_transform().get_position().y), radius=5)
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
