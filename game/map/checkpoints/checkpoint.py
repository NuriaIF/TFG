from game.entities.tile import Tile


class Checkpoint:
    def __init__(self, tile: Tile):
        self.assigned_tile = tile

    def get_assigned_tile(self):
        return self.assigned_tile

    def set_assigned_tile(self, tile):
        self.assigned_tile = tile
