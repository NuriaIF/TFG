from engine.managers.resource_manager.file_loader import FileLoader
from game.map.map_types_list import MapTypeList
from game.map.map_types import MapType

GLOBAL_MAP_PATH = "assets/tracks/"
MAP_EXTENSION = ".mlmap"



class MapLoader:
    @staticmethod
    def _char_to_tile(char: str) -> MapType:
        if char == 'o':
            return MapType.TRACK
        elif char == '\'':
            return MapType.GRASS
        elif char == '|':
            return MapType.SIDEWALK
        elif char == 'i':
            return MapType.CROSSWALK

    @staticmethod
    def load_map(map_name: str) -> MapTypeList:
        map_path = GLOBAL_MAP_PATH + map_name + MAP_EXTENSION
        text_map = FileLoader.load(map_path)
        mapWidth = len(text_map.split("\n")[0])
        mapHeight = len(text_map.split("\n"))
        loaded_map = MapTypeList(map_name, mapWidth, mapHeight)

        # Exception if it has more or less height than the map
        if len(text_map.split("\n")) != mapHeight:
            raise ValueError("Map height is not consistent")

        for line in text_map.split("\n"):
            # Exception if it has more or less width than the map
            if len(line) != mapWidth:
                raise ValueError("Map width is not consistent")

            for char in line:
                loaded_map.add_tile(MapLoader._char_to_tile(char))

        return loaded_map
