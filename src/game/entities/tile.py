"""
This module contains the Tile class
"""

from src.game.map.map_types import MapType


class Tile:
    """
    Class that encapsulates the tile entity in the game.
    It also contains the index on the map.
    """
    def __init__(self, entity: int, map_type: MapType, index_in_map: int, encoded_value: float):
        self.entity_ID = entity
        self.tile_type = map_type

        self.checkpoint_number = -1
        assert index_in_map >= 0
        self.index_in_map = index_in_map
        self._encoded_value = encoded_value

    def set_as_checkpoint(self, number: int) -> None:
        """
        Set the tile as a checkpoint
        Checkpoints are tiles that the car must reach in order to complete a lap
        :param number: checkpoint number
        :return: None
        """
        self.checkpoint_number = number

    def is_checkpoint(self) -> bool:
        """
        Check if the tile is a checkpoint
        Checkpoints are tiles that the car must reach in order to complete a lap
        :return: a boolean value indicating if the tile is a checkpoint
        """
        return self.checkpoint_number != -1

    def get_encoded_value(self):
        """
        Get the encoded value of the tile
        Encoded values are used by the AI to determine the value of the tile
        :return: the encoded value of the tile
        """
        return self._encoded_value
