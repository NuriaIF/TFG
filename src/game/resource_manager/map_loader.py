"""
This module is used to load maps from a file and return them as a MapTypeList
"""

from src.engine.managers.resource_manager.file_loader import FileLoader
from src.game.map.map_types_list import MapTypeList
from src.game.map.map_types import MapType

GLOBAL_MAP_PATH = "assets/tracks/"
MAP_EXTENSION = ".mlmap"


class MapLoader:
    """
    Maps are stored in a text file to be read.
    This class is used to read and load the map from that file and return it as a MapTypeList
    """
    @staticmethod
    def _char_to_tile(char: str) -> MapType:
        """
        Convert a character to a MapType
        There are 5 possible types of tiles:

        'o' Track

        'i' Crosswalk

        '|' Sidewalk

        '\'' Grass

        'T' Sea

        :param char: The character to convert
        :return: The MapType
        """
        if char == 'o':
            return MapType.TRACK
        elif char == '\'':
            return MapType.GRASS
        elif char == '|':
            return MapType.SIDEWALK
        elif char == 'i':
            return MapType.CROSSWALK
        elif char == 'T':
            return MapType.SEA

    @staticmethod
    def load_map(map_name: str) -> MapTypeList:
        """
        Load the map from a file and return it as a MapTypeList
        :param map_name: The name of the map to load
        :return: The map as a MapTypeList
        """
        map_path = GLOBAL_MAP_PATH + map_name + MAP_EXTENSION
        text_map = FileLoader.load(map_path)
        map_width = len(text_map.split("\n")[0])
        map_height = len(text_map.split("\n"))
        loaded_map = MapTypeList(map_name, map_width, map_height)

        # Exception if it has more or less height than the map
        if len(text_map.split("\n")) != map_height:
            raise ValueError("Map height is not consistent")

        for line in text_map.split("\n"):
            # Exception if it has more or less width than the map
            if len(line) != map_width:
                raise ValueError("Map width is not consistent")

            for char in line:
                loaded_map.add_tile(MapLoader._char_to_tile(char))

        return loaded_map
