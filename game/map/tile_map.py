from __future__ import annotations

import math

import numpy as np
from pygame import Vector2

from engine.engine import Engine
from engine.managers.entity_manager.entity_manager import EntityManager
from engine.managers.render_manager.render_layers import RenderLayer
from game.entities.tile import Tile
from game.map.checkpoints.checkpoints_loader import CheckpointsLoader
from game.map.map_loader import MapLoader
from game.map.map_types import MapType

TILE_SIZE = 16
MAP_WALL_DEPTH = 100


class TileMap:
    def __init__(self, engine: Engine, entity_manager: EntityManager):
        self.entity_manager = entity_manager

        self.tiles: list[Tile] = []
        self.type_map_list = MapLoader.load_map("road01-uni")

        self.checkpoints_dict = CheckpointsLoader.read_checkpoints("road01-uni")
        self.checkpoints: list[Tile] = []

        self.generate_tiles(engine)
        self.height = self.type_map_list.get_height() * TILE_SIZE
        self.width = self.type_map_list.get_width() * TILE_SIZE

        self._generate_walls(engine)

        self.positions = []
        self.tiles_fov = []
        self.ordered_tiles = []

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
                    tile.set_as_checkpoint(self.checkpoints_dict.get((index_x_pos, index_y_pos)))
                    self.checkpoints.append(tile)
            elif self.type_map_list[i] == MapType.GRASS:
                tile_entity = engine.create_entity("tiles/grass", background_batched=True, is_static=True)
                tile = Tile(tile_entity, MapType.GRASS)
            elif self.type_map_list[i] == MapType.SIDEWALK:
                tile_entity = engine.create_entity("tiles/sidewalk", background_batched=True, is_static=True)
                tile = Tile(tile_entity, MapType.SIDEWALK)
            elif self.type_map_list[i] == MapType.FOREST:
                tile_entity = engine.create_entity("tiles/forest", background_batched=True, is_static=True)
                tile = Tile(tile_entity, MapType.FOREST)
            elif self.type_map_list[i] == MapType.SEA:
                tile_entity = engine.create_entity("tiles/sea", background_batched=True, is_static=True)
                tile = Tile(tile_entity, MapType.SEA)
            else:
                tile_entity = engine.create_entity("tiles/road_centre_line", background_batched=True, is_static=True)
                tile = Tile(tile_entity, MapType.TRACK)

            # Set the tile's position
            self.entity_manager.get_transform(tile_entity).set_position(Vector2(x_pos, y_pos))

            self.tiles.append(tile)

    def _get_closest_tile(self, position: tuple[float, float], tiles: list[Tile], nearest_distance: float,
                          nearest_tile=None) -> Tile:
        for tile in tiles:
            tile_transform = self.entity_manager.get_transform(tile.entity_ID)
            distance = (tile_transform.get_position().x - position[0]) ** 2 + (
                    tile_transform.get_position().y - position[1]) ** 2
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_tile = tile
        return nearest_tile

    def _get_closest_tile_with_no_info(self, position: tuple[float, float]) -> Tile:
        return self._get_closest_tile(position, self.tiles, nearest_distance=float("inf"))

    def _get_closest_tile_knowing_previous(self, position: tuple[float, float], previous_nearest_tile: Tile) -> Tile:
        if previous_nearest_tile is None:
            return self._get_closest_tile_with_no_info(position)
        # Verify if the previous tile is still the nearest
        tile_transform = self.entity_manager.get_transform(previous_nearest_tile.entity_ID)
        prev_distance = (tile_transform.get_position().x - position[0]) ** 2 + \
                        (tile_transform.get_position().y - position[1]) ** 2

        nearest_tile = previous_nearest_tile
        nearest_distance = prev_distance

        # Obtain adjacent tiles to previous_nearest_tile and include previous_nearest_tile in the search
        adjacent_tiles = self._get_adjacent_tiles(previous_nearest_tile)

        adjacent_tiles.append(previous_nearest_tile)

        nearest_tile = self._get_closest_tile(position, adjacent_tiles, nearest_distance=nearest_distance,
                                              nearest_tile=nearest_tile)

        return nearest_tile

    def _get_adjacent_tiles(self, tile: Tile) -> list[Tile]:
        adjacent_tiles = []
        tile_index = self.tiles.index(tile)
        map_width = self.type_map_list.get_width()
        for i in range(-1, 2):
            for j in range(-1, 2):
                if 0 <= tile_index + i + j * map_width < len(self.tiles):
                    adjacent_tiles.append(self.tiles[tile_index + i + j * map_width])
        return adjacent_tiles

    def get_tile(self, x, y):
        map_width = self.type_map_list.get_width()
        if 0 <= x < map_width and 0 <= y < self.height:
            return self.tiles[y * map_width + x]
        return None

    def get_tiles_within_square(self, position: tuple[float, float], previous_nearest_tile, radius: int,
                                vision_box: list[Vector2], angle: int) -> (list[Tile], Tile):
        within_square: list[Tile] = []
        tile = self._get_closest_tile_knowing_previous(position, previous_nearest_tile)
        tile_index = self.tiles.index(tile)
        map_width = self.type_map_list.get_width()
        map_height = len(self.tiles) // map_width

        r = radius + radius // 3
        min_j = max(-r, -tile_index // map_width)
        max_j = min(r, map_height - tile_index // map_width)

        for j in range(min_j, max_j):
            for i in range(-r, r):
                current_index = tile_index + i + j * map_width
                if 0 <= current_index < len(self.tiles):
                    tile_transform = self.entity_manager.get_transform(self.tiles[current_index].entity_ID)
                    tile_position = tile_transform.get_position()
                    if self._point_in_polygon(tile_position, vision_box):
                        within_square.append(self.tiles[current_index])

        if radius == 6:
            tile_transform = self.entity_manager.get_transform(tile.entity_ID)
            tile_position = tile_transform.get_position()
            within_square = self._order_tiles(within_square, angle, position=tile_position)
            if len(within_square) > 144:
                within_square = within_square[:144]

        return within_square, tile

    def _order_tiles(self, tiles, angle, position) -> list[Tile]:
        theta = math.radians(angle) - math.pi / 2

        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)

        rotation_matrix = [
            [cos_theta, sin_theta],
            [-sin_theta, cos_theta]
        ]

        ordered_tiles = []
        position_and_tile_list = []

        self.positions = []

        position = Vector2(position)

        for tile in tiles:
            if tile is not None:
                transform = self.entity_manager.get_transform(tile.entity_ID)
                tile_pos: Vector2 = transform.get_position()
                relative_tile_pos = position - tile_pos
                rotated_tile_pos = Vector2(
                    relative_tile_pos.x * rotation_matrix[0][0] + relative_tile_pos.y * rotation_matrix[0][1],
                    relative_tile_pos.x * rotation_matrix[1][0] + relative_tile_pos.y * rotation_matrix[1][1]
                )
                position_and_tile_list.append((rotated_tile_pos, tile))

        # Sort the list by y
        position_and_tile_list.sort(key=lambda item: item[0].y)

        # Group the list in sublists of 12 elements
        grouped_arrays = [position_and_tile_list[i:i + 12] for i in range(0, len(position_and_tile_list), 12)]

        # Sort each sublist by x
        for sublist in grouped_arrays:
            sublist.sort(key=lambda item: item[0].x)
            ordered_tiles.extend([tile for _, tile in sublist])
            self.positions.extend([pos for pos, _ in sublist])

        return ordered_tiles

    def _point_in_polygon(self, point, polygon):
        intersection_x = 0
        x, y = point
        n = len(polygon)
        inside = False

        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if p1y < y <= p2y or p2y < y <= p1y:
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        intersection_x = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= intersection_x:
                        inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    def _generate_walls(self, engine: Engine) -> None:
        border_width = TILE_SIZE * 8
        # Create large entities that surround the map that have colliders, so the car can't leave the map
        upper_wall = engine.create_entity("tiles/map_border_center", has_collider=True, is_static=True)
        upper_wall_transform = self.entity_manager.get_transform(upper_wall)
        upper_wall_transform.set_position(
            Vector2(self.type_map_list.get_width() * TILE_SIZE / 2, -TILE_SIZE + border_width))
        self.entity_manager.set_layer(upper_wall, RenderLayer.TILES)
        self.entity_manager.get_collider(upper_wall).debug_config_show_collider()

        bottom_wall = engine.create_entity("tiles/map_border_center", has_collider=True, is_static=True)
        bottom_wall_transform = self.entity_manager.get_transform(bottom_wall)
        bottom_wall_transform.set_position(
            Vector2(self.type_map_list.get_width() * TILE_SIZE / 2, self.height - border_width))
        bottom_wall_transform.rotate(180)
        self.entity_manager.set_layer(bottom_wall, RenderLayer.TILES)
        self.entity_manager.get_collider(bottom_wall).debug_config_show_collider()

        left_wall = engine.create_entity("tiles/map_border_lateral", has_collider=True, is_static=True)
        left_wall_transform = self.entity_manager.get_transform(left_wall)
        left_wall_transform.set_position(Vector2(-TILE_SIZE + border_width, self.height / 2))
        self.entity_manager.set_layer(left_wall, RenderLayer.TILES)
        self.entity_manager.get_collider(left_wall).debug_config_show_collider()

        right_wall = engine.create_entity("tiles/map_border_lateral", has_collider=True, is_static=True)
        right_wall_transform = self.entity_manager.get_transform(right_wall)
        right_wall_transform.set_position(Vector2(self.width - border_width, self.height / 2))
        right_wall_transform.rotate(180)
        self.entity_manager.set_layer(right_wall, RenderLayer.TILES)
        self.entity_manager.get_collider(right_wall).debug_config_show_collider()

    def get_checkpoint_in(self, area: list[Tile]) -> int:
        """
        Check if the area contains a checkpoint and return the checkpoint number
        :param area: 
        :return: 
        """
        for tile in area:
            if tile.is_checkpoint():
                return tile.checkpoint_number

    def get_next_checkpoint_position(self, checkpoint: int) -> tuple[float, float]:
        if checkpoint is None:
            return float('inf'), float('inf')
        next_checkpoint_number = checkpoint + 1
        for tile in self.checkpoints:
            if tile.checkpoint_number == next_checkpoint_number:
                tile_transform = self.entity_manager.get_transform(tile.entity_ID)
                return tile_transform.get_position().x, tile_transform.get_position().y
        return float('inf'), float('inf')

