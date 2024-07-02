from enum import Enum


class MapType(Enum):
    TRACK = 1
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


class EncodedValue(Enum):
    TRACK = 1.0
    CROSSWALK = 1.0
    SIDEWALK = -0.5
    GRASS = -1.0
    FOREST = -1.0
    SEA = -2.0


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


def map_type_to_encoded_value(map_type: MapType) -> float:
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
