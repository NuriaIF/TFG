from __future__ import annotations

import math

import numpy as np
from pygame import Vector2, Rect

from engine.engine import Engine
from engine.managers.render_manager.render_layers import RenderLayer
from game.entities.tile import Tile
from game.map.checkpoints.checkpoints_loader import CheckpointsLoader
from game.map.map_loader import MapLoader
from game.map.map_types import MapType

TILE_SIZE = 16
MAP_WALL_DEPTH = 100


class TileMap:
    def __init__(self, engine: Engine):
        self.tiles: list[Tile] = []
        self.type_map_list = MapLoader.load_map("road01-uni")

        self.checkpoints_dict = CheckpointsLoader.read_checkpoints("road01-uni")
        self.checkpoints: list[Tile] = []

        self.generate_tiles(engine)
        self.height = self.type_map_list.get_height() * TILE_SIZE
        self.width = self.type_map_list.get_width() * TILE_SIZE

        self.generate_walls(engine)

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
            tile_entity.get_transform().set_position(Vector2(x_pos, y_pos))

            # self.tiles[(x_pos, y_pos)] = tile_entity
            self.tiles.append(tile)

    # def get_closest_tile(self, position: tuple[int, int]) -> Entity:
    #     remaining = (position[0] % TILE_SIZE, position[1] % TILE_SIZE)
    #     closest_tile_pos = (position[0] - remaining[0], position[1] - remaining[1])
    #     return self.tiles[closest_tile_pos]

    def get_closest_tile_with_no_info(self, position: tuple[float, float]) -> Tile:
        nearest_distance = float("inf")
        nearest_tile = None
        for tile in self.tiles:
            distance = (tile.tile_entity.get_transform().get_position().x - position[0]) ** 2 + (
                    tile.tile_entity.get_transform().get_position().y - position[1]) ** 2
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_tile = tile
        return nearest_tile

    def get_closest_tile_knowing_previous(self, position: tuple[float, float], previous_nearest_tile: Tile) -> Tile:
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

    def get_tiles_in(self, position: tuple[float, float]) -> Tile:
        nearest_distance = float("inf")
        nearest_tile = None
        for tile in self.tiles:
            distance = (tile.tile_entity.get_transform().get_position().x - position[0]) ** 2 + (
                    tile.tile_entity.get_transform().get_position().y - position[1]) ** 2
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_tile = tile
        return nearest_tile

    def get_tile(self, x, y):
        map_width = self.type_map_list.get_width()
        if 0 <= x < map_width and 0 <= y < self.height:
            return self.tiles[y * map_width + x]
        return None

    def get_tiles_within_square(self, position: tuple[float, float], previous_nearest_tile, radius: int,
                                forward: Vector2) \
            -> (list[Tile], Tile):
        radius_in_pixels = radius * TILE_SIZE
        vision_rect = Rect(position[0] - radius_in_pixels, position[1] - radius_in_pixels, 192, 192)

        center = Vector2([vision_rect.centerx, vision_rect.centery])

        points = [
            Vector2([vision_rect.topleft[0], vision_rect.topleft[1]]),
            Vector2([vision_rect.topright[0], vision_rect.topright[1]]),
            Vector2([vision_rect.bottomright[0], vision_rect.bottomright[1]]),
            Vector2([vision_rect.bottomleft[0], vision_rect.bottomleft[1]])
        ]
        angle = np.degrees(np.arctan2(forward.y, forward.x))

        rotated_points: list[Vector2] = [self.rotate_point(point, center, angle) for point in points]
        # get the tiles that are in the area defined by rotated_points
        within_square: list[Tile] = []
        tile = self.get_closest_tile_knowing_previous(position, previous_nearest_tile)
        tile_index = self.tiles.index(tile)
        map_width = self.type_map_list.get_width()
        for j in range(-radius * 2, radius * 2):
            for i in range(-radius * 2, radius * 2):
                if 0 <= tile_index + i + j * map_width < len(self.tiles):
                    position = self.tiles[tile_index + i + j * map_width].tile_entity.get_transform().get_position()
                    tile_pos = tile_index + i + j * map_width
                    if self.point_in_polygon(position, rotated_points):
                        within_square.append(self.tiles[tile_pos])

        if radius == 6:
            tile_position = tile.tile_entity.get_transform().get_position()
            within_square = self.order_tiles(within_square, angle, position=tile_position)
            if len(within_square) > 144:
                within_square = within_square[:144]
        return within_square, tile

    def order_tiles(self, tiles, angle, position):
        theta = np.radians(angle)
        theta = theta - np.pi / 2

        rotation_matrix = [[np.cos(theta), np.sin(theta)],
                           [-np.sin(theta), np.cos(theta)]]

        ordered_tiles = []
        position_and_tile_list = []

        self.positions = []

        position = Vector2(position)

        for tile in tiles:
            if tile is not None:
                tile_pos: Vector2 = tile.tile_entity.get_transform().get_position()
                tile_pos = position - tile_pos
                # apply rotation matrix to tile relative position
                tile_pos = np.dot(rotation_matrix, tile_pos)
                # self.positions.append(tile_pos)
                position_and_tile_list.append((tile_pos, tile))

        # Sort the list by y
        position_and_tile_list.sort(key=lambda arr: arr[0][1])

        # Group the list in sublists of 12 elements
        grouped_arrays = [position_and_tile_list[i:i + 12] for i in range(0, len(position_and_tile_list), 12)]

        # Sort each sublist by x
        for sublist in grouped_arrays:
            sublist.sort(key=lambda arr: arr[0][0])
            ordered_tiles.extend([tile for _, tile in sublist])
            self.positions.extend([pos for pos, _ in sublist])
        return ordered_tiles

    def point_in_polygon(self, point, polygon):
        intersection_x = 0
        x, y = point
        n = len(polygon)
        inside = False

        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            intersection_x = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= intersection_x:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    def rotate_point(self, point, center, angle) -> Vector2:
        angle_rad = np.deg2rad(angle)
        cos_angle = np.cos(angle_rad)
        sin_angle = np.sin(angle_rad)
        translated_point = point - center
        rotated_point = np.dot(np.array([
            [cos_angle, -sin_angle],
            [sin_angle, cos_angle]
        ]), translated_point)
        rotated_point = Vector2([rotated_point[0], rotated_point[1]])
        return rotated_point + center

    def generate_walls(self, engine: Engine) -> None:
        border_width = TILE_SIZE * 8
        # Create large entities that surround the map that have colliders, so the car can't leave the map
        upper_wall = engine.create_entity("tiles/map_border_center", has_collider=True, is_static=True)
        upper_wall.get_transform().set_position(Vector2(self.type_map_list.get_width() * TILE_SIZE / 2, -TILE_SIZE + border_width))
        upper_wall.set_layer(RenderLayer.TILES)
        upper_wall.debug_config_show_collider()

        bottom_wall = engine.create_entity("tiles/map_border_center", has_collider=True, is_static=True)
        bottom_wall.get_transform().set_position(
            Vector2(self.type_map_list.get_width() * TILE_SIZE / 2, self.height - border_width))
        bottom_wall.get_transform().rotate(180)
        bottom_wall.set_layer(RenderLayer.TILES)
        bottom_wall.debug_config_show_collider()

        left_wall = engine.create_entity("tiles/map_border_lateral", has_collider=True, is_static=True)
        left_wall.get_transform().set_position(Vector2(-TILE_SIZE + border_width, self.height / 2))
        left_wall.set_layer(RenderLayer.TILES)
        left_wall.debug_config_show_collider()

        right_wall = engine.create_entity("tiles/map_border_lateral", has_collider=True, is_static=True)
        right_wall.get_transform().set_position(Vector2(self.width - border_width, self.height / 2))
        right_wall.get_transform().rotate(180)
        right_wall.set_layer(RenderLayer.TILES)
        right_wall.debug_config_show_collider()

    def get_checkpoint_in(self, area: list[Tile]) -> int:
        """
        Check if the area contains a checkpoint and return the checkpoint number
        :param area: 
        :return: 
        """
        for tile in area:
            if tile.is_checkpoint():
                return tile.checkpoint_number

    def get_distance_to_next_checkpoint(self, checkpoint: int, position: tuple[float, float]) -> float:
        if checkpoint is None:
            return float('inf')
        next_checkpoint_number = checkpoint + 1
        for tile in self.checkpoints:
            if tile.checkpoint_number == next_checkpoint_number:
                distance = math.sqrt((tile.tile_entity.get_transform().get_position().x - position[0]) ** 2 +
                                     (tile.tile_entity.get_transform().get_position().y - position[1]) ** 2)
                return distance
        return float('inf')
    
    def get_next_checkpoint_position(self, checkpoint: int) -> tuple[float, float]:
        if checkpoint is None:
            return float('inf'), float('inf')
        next_checkpoint_number = checkpoint + 1
        for tile in self.checkpoints:
            if tile.checkpoint_number == next_checkpoint_number:
                return tile.tile_entity.get_transform().get_position().x, tile.tile_entity.get_transform().get_position().y
        return float('inf'), float('inf')

    def get_angle_to_next_checkpoint(self, checkpoint: int, position: tuple[float, float]) -> float:
        if checkpoint is None:
            return float('inf')
        next_checkpoint_number = checkpoint + 1
        for tile in self.checkpoints:
            if tile.checkpoint_number == next_checkpoint_number:
                angle = math.degrees(math.atan2(tile.tile_entity.get_transform().get_position().y - position[1],
                                                tile.tile_entity.get_transform().get_position().x - position[0]))
                return angle
        return float('inf')
