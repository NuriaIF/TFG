from game.map.map_types import MapType


class Tile:
    def __init__(self, entity: int, map_type: MapType):
        self.entity_ID = entity
        self.tile_type = map_type

        self.checkpoint_number = -1

    def set_as_checkpoint(self, number: int):
        self.checkpoint_number = number

    def is_checkpoint(self):
        return self.checkpoint_number != -1
