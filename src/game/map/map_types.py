"""
This module contains the MapType enum.
"""
from enum import Enum


class MapType(Enum):
    """
    Enum class for the type of tile in the map
    """
    TRACK = 1
    CROSSWALK = 2
    SIDEWALK = 3
    GRASS = 4
    FOREST = 5
    SEA = 6


class MapTypeFile(Enum):
    """
    This enum class is used to map the MapType to the file that contains the information of the tile
    """
    TRACK = "track"
    CROSSWALK = "crosswalk"
    SIDEWALK = "sidewalk"
    GRASS = "grass"
    FOREST = "forest"
    SEA = "sea"


class EncodedValue(Enum):
    """
    This enum class is used to map the MapType to the encoded value of the tile
    The encodings are used to train the AI
    """
    TRACK = 1.0
    CROSSWALK = 1.0
    SIDEWALK = -0.5
    GRASS = -1.0
    FOREST = -1.0
    SEA = -2.0


def map_type_to_file(map_type: MapType) -> str:
    """
    This function maps the MapType to the file that contains the information of the tile
    :param map_type: The type of tile
    :return: The file that contains the information of the tile
    """
    if map_type == MapType.TRACK:
        return str(MapTypeFile.TRACK.value)
    elif map_type == MapType.CROSSWALK:
        return str(MapTypeFile.CROSSWALK.value)
    elif map_type == MapType.SIDEWALK:
        return str(MapTypeFile.SIDEWALK.value)
    elif map_type == MapType.GRASS:
        return str(MapTypeFile.GRASS.value)
    elif map_type == MapType.FOREST:
        return str(MapTypeFile.FOREST.value)
    elif map_type == MapType.SEA:
        return str(MapTypeFile.SEA.value)


def map_type_to_encoded_value(map_type: MapType) -> float:
    """
    This function maps the MapType to the encoded value of the tile
    :param map_type: The type of tile
    :return: The encoded value of the tile
    """
    if map_type == MapType.TRACK:
        return float(EncodedValue.TRACK.value)
    elif map_type == MapType.CROSSWALK:
        return float(EncodedValue.CROSSWALK.value)
    elif map_type == MapType.SIDEWALK:
        return float(EncodedValue.SIDEWALK.value)
    elif map_type == MapType.GRASS:
        return float(EncodedValue.GRASS.value)
    elif map_type == MapType.FOREST:
        return float(EncodedValue.FOREST.value)
    elif map_type == MapType.SEA:
        return float(EncodedValue.SEA.value)
