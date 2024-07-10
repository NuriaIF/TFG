"""
This module is used to store the map of the game
"""

from src.game.map.map_types import MapType


class MapTypeList:
    """
    This class is used to store the map of the game
    It stores the map name, the width and the height of the map and the tile map as a list of MapType (enum)
    """
    def __init__(self, map_name: str, width: int, height: int) -> None:
        """
        Initialize the map type list
        :param map_name: The name of the map
        :param width: The width of the map
        :param height: The height of the map
        """
        self.width = width
        self.height = height
        self.map_name = map_name
        self.tile_map = []

    def __getitem__(self, index: int) -> MapType:
        """
        Get the tile at the index of the tile map
        :param index: The index of the tile in the tile map
        :return: The tile at the index
        """
        return self.tile_map[index]

    def __setitem__(self, index: int, value: MapType) -> None:
        """
        Set the tile at the index of the tile map
        :param index: The index of the tile
        :param value: The value of the tile
        :return: None
        """
        self.tile_map[index] = value

    def __len__(self) -> int:
        """
        Get the length of the tile map
        :return:
        """
        return len(self.tile_map)

    def add_tile(self, tile: MapType) -> None:
        """
        Add a tile to the tile map
        :param tile: The tile to add
        :return: None
        """
        self.tile_map.append(tile)

    def get_tile_map(self) -> list[MapType]:
        """
        Get the tile map
        :return: The tile map
        """
        return self.tile_map

    def get_map_name(self) -> str:
        """
        Get the name of the map
        :return: The name of the map
        """
        return self.map_name

    def set_map_name(self, map_name) -> None:
        """
        Set the name of the map
        :param map_name: The name of the map
        :return: None
        """
        self.map_name = map_name

    def set_width(self, width) -> None:
        """
        Set the width of the map
        :param width: The width of the map
        :return: None
        """
        self.width = width

    def set_height(self, height) -> None:
        """
        Set the height of the map
        :param height: The height of the map
        :return: None
        """
        self.height = height

    def get_width(self) -> int:
        """
        Get the width of the map
        :return: The width of the map
        """
        return self.width

    def get_height(self) -> int:
        """
        Get the height of the map
        :return: The height of the map
        """
        return self.height
