from game.map.map_types import MapType


class Map:
    def __init__(self, map_name: str, width: int, height: int):
        self.width = width
        self.height = height
        self.map_name = map_name
        self.tile_map = []

    def __getitem__(self, index: int) -> MapType:
        return self.tile_map[index]

    def __setitem__(self, index: int, value: MapType) -> None:
        self.tile_map[index] = value

    def __len__(self) -> int:
        return len(self.tile_map)

    def add_tile(self, tile: MapType) -> None:
        self.tile_map.append(tile)

    def get_tile_map(self) -> list[MapType]:
        return self.tile_map

    def get_map_name(self) -> str:
        return self.map_name

    def set_map_name(self, map_name):
        self.map_name = map_name

    def set_width(self, width) -> None:
        self.width = width

    def set_height(self, height) -> None:
        self.height = height

    def get_width(self) -> int:
        return self.width

    def get_height(self) -> int:
        return self.height
