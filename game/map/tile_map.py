import math

from pygame import Vector2

from engine.engine import Engine
from engine.managers.render_manager.render_layers import RenderLayer
from game.map.checkpoints.checkpoint import Checkpoint
from game.map.checkpoints.checkpoints_loader import CheckpointsLoader
from game.map.map_loader import MapLoader
from game.map.map_types import MapType
from game.entities.tile import Tile

TILE_SIZE = 16
MAP_WALL_DEPTH = 100


class TileMap:
    def __init__(self, engine: Engine):
        # Map position -> tile
        # self.tiles: dict[tuple[int, int], Entity] = {}
        # self.tiles: set[Tile] = set()
        self.tiles: list[Tile] = []
        self.type_map_list = MapLoader.load_map("road01-uni")

        self.checkpoints: list[Checkpoint] = []
        self.checkpoints_dict = CheckpointsLoader.read_checkpoints("road01-uni")

        self.generate_tiles(engine)
        self.height = self.type_map_list.get_height() * TILE_SIZE
        self.width = self.type_map_list.get_width() * TILE_SIZE

        self.generate_walls(engine)

    def generate_tiles(self, engine: Engine) -> None:
        for i in range(len(self.type_map_list)):
            x_pos = (i % self.type_map_list.get_width()) * TILE_SIZE
            y_pos = (i // self.type_map_list.get_width()) * TILE_SIZE

            index_x_pos = i % self.type_map_list.get_width()
            index_y_pos = i // self.type_map_list.get_width()
            # print(index_x_pos, index_y_pos, self.type_map_list[i])

            if self.type_map_list[i] == MapType.TRACK:
                tile_entity = engine.create_entity("tiles/track", background_batched=True, is_static=True)
                tile = Tile(tile_entity, MapType.TRACK)
                if self.checkpoints_dict.get((index_x_pos, index_y_pos)) is not None:
                    self.checkpoints.append(Checkpoint(tile))
            elif self.type_map_list[i] == MapType.GRASS:
                tile_entity = engine.create_entity("tiles/grass", background_batched=True, is_static=True)
                tile = Tile(tile_entity, MapType.GRASS)
            elif self.type_map_list[i] == MapType.SIDEWALK:
                tile_entity = engine.create_entity("tiles/sidewalk", background_batched=True, is_static=True)
                tile = Tile(tile_entity, MapType.SIDEWALK)
            elif self.type_map_list[i] == MapType.FOREST:
                tile_entity = engine.create_entity("tiles/forest", background_batched=True, is_static=True)
                tile = Tile(tile_entity, MapType.FOREST)
            else:
                tile_entity = engine.create_entity("tiles/road_centre_line", background_batched=True, is_static=True)
                tile = Tile(tile_entity, MapType.TRACK)

            # Set the tile's position
            tile_entity.get_transform().set_position(Vector2(x_pos, y_pos))

            # self.tiles[(x_pos, y_pos)] = tile_entity
            self.tiles.append(tile)

    # def get_closest_tile(self, position: tuple[int, int]) -> Entity:
    #     remaining = (position[0] % TILE_SIZE, position[1] % TILE_SIZE)
    #     closest_tile_pos = (position[0] - remaining[0], position[1] - remaining[1])
    #     return self.tiles[closest_tile_pos]

    def get_closest_tile_with_no_info(self, position: tuple[int, int]) -> Tile:
        nearest_distance = float("inf")
        nearest_tile = None
        for tile in self.tiles:
            distance = (tile.tile_entity.get_transform().get_position().x - position[0]) ** 2 + (
                    tile.tile_entity.get_transform().get_position().y - position[1]) ** 2
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_tile = tile
        return nearest_tile

    def get_closest_tile_knowing_previous(self, position: tuple[int, int], previous_nearest_tile: Tile) -> Tile:
        if previous_nearest_tile is None:
            return self.get_closest_tile_with_no_info(position)
        # Verify if the previous tile is still the nearest
        prev_distance = (previous_nearest_tile.tile_entity.get_transform().get_position().x - position[0]) ** 2 + \
                        (previous_nearest_tile.tile_entity.get_transform().get_position().y - position[1]) ** 2

        nearest_tile = previous_nearest_tile
        nearest_distance = prev_distance

        # Obtain adjacent tiles to previous_nearest_tile and include previous_nearest_tile in the search
        adjacent_tiles = self.get_adjacent_tiles(previous_nearest_tile)

        adjacent_tiles.append(previous_nearest_tile)

        for tile in adjacent_tiles:
            distance = (tile.tile_entity.get_transform().get_position().x - position[0]) ** 2 + \
                       (tile.tile_entity.get_transform().get_position().y - position[1]) ** 2
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_tile = tile

        return nearest_tile

    def get_adjacent_tiles(self, tile: Tile) -> list[Tile]:
        adjacent_tiles = []
        tile_index = self.tiles.index(tile)
        map_width = self.type_map_list.get_width()
        for i in range(-1, 2):
            for j in range(-1, 2):
                if 0 <= tile_index + i + j * map_width < len(self.tiles):
                    adjacent_tiles.append(self.tiles[tile_index + i + j * map_width])
        return adjacent_tiles

    def get_tiles_in(self, position: tuple[int, int]) -> Tile:
        nearest_distance = float("inf")
        nearest_tile = None
        for tile in self.tiles:
            distance = (tile.tile_entity.get_transform().get_position().x - position[0]) ** 2 + (
                    tile.tile_entity.get_transform().get_position().y - position[1]) ** 2
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_tile = tile
        return nearest_tile

    def get_tiles_within_square(self, position: tuple[float, float], previous_nearest_tile, radius: int):
        map_width = self.type_map_list.get_width()
        within_square: list[Tile | None] = []
        tile = self.get_closest_tile_knowing_previous(position, previous_nearest_tile)
        tile_index = self.tiles.index(tile)
        for i in range(-radius, radius):
            for j in range(-radius, radius):
                if 0 <= tile_index + i + j * map_width < len(self.tiles):
                    within_square.append(self.tiles[tile_index + i + j * map_width])
                else:
                    within_square.append(None)
        return within_square, tile

    def generate_walls(self, engine: Engine) -> None:
        # Create large entities that surround the map that have colliders, so the car can't leave the map
        upper_wall = engine.create_entity("tiles/map_border_center", has_collider=True, is_static=True)
        upper_wall.get_transform().set_position(Vector2(upper_wall.get_sprite_rect().width / 2 - TILE_SIZE, -TILE_SIZE))
        upper_wall.set_layer(RenderLayer.TILES)
        upper_wall.debug_config_show_collider()

        bottom_wall = engine.create_entity("tiles/map_border_center", has_collider=True, is_static=True)
        bottom_wall.get_transform().set_position(
            Vector2(self.type_map_list.get_width() * TILE_SIZE / 2, self.height))
        bottom_wall.get_transform().rotate(180)
        bottom_wall.set_layer(RenderLayer.TILES)
        bottom_wall.debug_config_show_collider()

        right_wall = engine.create_entity("tiles/map_border_lateral", has_collider=True, is_static=True)
        right_wall.get_transform().set_position(Vector2(-TILE_SIZE, self.height / 2))
        right_wall.set_layer(RenderLayer.TILES)
        right_wall.debug_config_show_collider()

        left_wall = engine.create_entity("tiles/map_border_lateral", has_collider=True, is_static=True)
        left_wall.get_transform().set_position(Vector2(self.width, self.height / 2))
        left_wall.get_transform().rotate(180)
        left_wall.set_layer(RenderLayer.TILES)
        left_wall.debug_config_show_collider()
