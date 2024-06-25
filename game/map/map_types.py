from enum import Enum


class MapType(Enum):
    TRACK = 1
    # WALL = 2
    # GOAL = 3
    CROSSWALK = 2
    SIDEWALK = 3
    GRASS = 4
    FOREST = 5
    SEA = 6


class MapTypeFile(Enum):
    TRACK = "track"
    CROSSWALK = "crosswalk"
    SIDEWALK = "sidewalk"
    GRASS = "grass"
    FOREST = "forest"
    SEA = "sea"


def map_type_to_file(map_type: MapType) -> str:
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
