from engine.entities.entity import Entity
from game.map.map_types import MapType


class Tile:
    def __init__(self, entity: Entity, map_type: MapType):
        self.tile_entity = entity
        self.tile_type = map_type

