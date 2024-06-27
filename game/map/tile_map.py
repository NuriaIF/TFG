from __future__ import annotations

import math

from pygame import Vector2

from engine.engine import Engine
from engine.managers.entity_manager.entity_manager import EntityManager
from engine.managers.render_manager.render_layers import RenderLayer
from game.entities.tile import Tile
from game.map.checkpoints.checkpoint_direction import CheckpointDirection
from game.map.checkpoints.checkpoints_loader import CheckpointsLoader
from game.map.map_loader import MapLoader
from game.map.map_types import MapType
from game.map.map_types import map_type_to_file

TILE_SIZE = 16
MAP_WALL_DEPTH = 100


class TileMap:
    def __init__(self, engine: Engine, entity_manager: EntityManager):
        self.entity_manager = entity_manager

        self.tiles: list[Tile] = []
        self.type_map_list = MapLoader.load_map("road01-uni")

        self.checkpoints_info = CheckpointsLoader.read_checkpoints("road01-uni")
        self.checkpoints_dict = self.checkpoints_info[0]
        self.checkpoints_directions_dict = self.checkpoints_info[1]
        self.checkpoints: list[Tile] = []
        self.checkpoint_lines: list[Tile] = []

        self.generate_tiles(engine)
        self.height = self.type_map_list.get_height() * TILE_SIZE
        self.width = self.type_map_list.get_width() * TILE_SIZE

        self._generate_walls(engine)

        self.positions = []
        self.tiles_fov = []
        self.ordered_tiles = []

    def get_width_number(self):
        return self.type_map_list.get_width()

    def get_height_number(self):
        return self.type_map_list.get_height()

    def generate_tiles(self, engine: Engine) -> None:
        for i in range(len(self.type_map_list)):
            x_pos = (i % self.type_map_list.get_width()) * TILE_SIZE
            y_pos = (i // self.type_map_list.get_width()) * TILE_SIZE

            index_x_pos = i % self.type_map_list.get_width()
            index_y_pos = i // self.type_map_list.get_width()

            map_type = self.type_map_list[i]
            map_file = map_type_to_file(map_type)
            tile_entity = self.entity_manager.create_entity("tiles/" + map_file, batched=True, is_static=True)
            tile = Tile(tile_entity, map_type, i)
            if self.type_map_list[i] == MapType.TRACK:
                if self.checkpoints_dict.get((index_x_pos, index_y_pos)) is not None:
                    tile.set_as_checkpoint(self.checkpoints_dict.get((index_x_pos, index_y_pos)))
                    self.checkpoints.append(tile)
            # Set the tile's position
            self.entity_manager.get_transform(tile_entity).set_position(Vector2(x_pos, y_pos))

            self.tiles.append(tile)

        self.process_checkpoints()

    def get_tile_at_pos(self, vec2: Vector2) -> Tile:
        [index_x, index_y] = self.get_tile_index_from_pos(vec2)
        return self.get_tile(index_x, index_y)

    def get_tile_index_from_pos(self, position: Vector2) -> [int, int]:
        return int(position.x // TILE_SIZE), int(position.y // TILE_SIZE)

    def get_tiles_within_square(self, position: tuple[float, float], radius: float, vision_box: list[Vector2],
                                angle: float) -> list[Tile]:
        tiles: list[Tile] = []
        tiles_size: int = round((radius * 2 * radius * 2)) // TILE_SIZE
        for i in range(-tiles_size, tiles_size):
            for j in range(-tiles_size, tiles_size):
                tile = self.get_tile_at_pos(Vector2(int(position[0] + i * TILE_SIZE), int(position[1] + j * TILE_SIZE)))
                if tile is not None:
                    if self._point_in_polygon(self.entity_manager.get_transform(tile.entity_ID).get_position(),
                                              vision_box):
                        tiles.append(tile)
        if radius == 6:
            tiles = self._order_tiles(tiles, angle, position=Vector2(position))
            tiles = tiles[:144]
        return tiles

    def get_tiles_of_rect(self, position: tuple[float, float], radius: float, vision_box: list[Vector2]) -> list[Tile]:
        tiles: list[Tile] = []
        tiles_size: int = round((radius * 2 * radius * 2)) // TILE_SIZE
        if tiles_size < 1:
            tiles_size = 2
        for i in range(-tiles_size, tiles_size):
            for j in range(-tiles_size, tiles_size):
                tile_pos: Vector2 = Vector2(int(position[0] + i * TILE_SIZE), int(position[1] + j * TILE_SIZE))
                # # Check out of bounds
                # if 0 <= tile_pos.x < self.width - 1 and 0 <= tile_pos.y < self.height - 1:
                #     continue
                tile = self.get_tile_at_pos(tile_pos)
                if tile is not None:
                    position_tile = self.entity_manager.get_transform(tile.entity_ID).get_position()
                    edge_upper_left = Vector2(position_tile.x + 1, position_tile.y + 1)
                    edge_upper_right = Vector2(position_tile.x + TILE_SIZE - 1, position_tile.y + 1)
                    edge_bottom_left = Vector2(position_tile.x + 1, position_tile.y + TILE_SIZE - 1)
                    edge_bottom_right = Vector2(position_tile.x + TILE_SIZE - 1, position_tile.y + TILE_SIZE - 1)
                    if (self._point_in_polygon(edge_upper_left, vision_box) or
                            self._point_in_polygon(edge_upper_right, vision_box) or
                            self._point_in_polygon(edge_bottom_left, vision_box) or
                            self._point_in_polygon(edge_bottom_right, vision_box)):
                        tiles.append(tile)
        return tiles

    def set_checkpoint_line(self, start_index, offset_func, checkpoint_number):
        for j in range(-2, 3):
            index = offset_func(start_index, j)
            if 0 <= index < len(self.tiles):
                self.tiles[index].set_as_checkpoint(checkpoint_number)
                self.checkpoint_lines.append(self.tiles[index])

    def get_offset_func(self, direction):
        width = self.type_map_list.get_width()
        if direction == CheckpointDirection.HORIZONTAL:
            return lambda idx, j: idx + j
        elif direction == CheckpointDirection.VERTICAL:
            return lambda idx, j: idx + j * width
        elif direction == CheckpointDirection.DIAGONAL_LEFT:
            return lambda idx, j: idx + j * width + j
        elif direction == CheckpointDirection.DIAGONAL_RIGHT:
            return lambda idx, j: idx + j * width - j
        else:
            raise ValueError(f"Unknown direction: {direction}")

    def process_checkpoints(self):
        for tile in self.checkpoints:
            direction = self.checkpoints_directions_dict[tile.checkpoint_number]
            offset_func = self.get_offset_func(direction)
            self.set_checkpoint_line(tile.index_in_map, offset_func, tile.checkpoint_number)

    def get_tile(self, x, y):
        map_width = self.type_map_list.get_width()
        map_height = self.type_map_list.get_height()
        if 0 <= x < map_width and 0 <= y < map_height:
            return self.tiles[y * map_width + x]
        return None

    def _order_tiles(self, tiles: list[Tile], angle: float, position: Vector2) -> list[Tile]:
        theta = math.radians(angle) - math.pi

        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)

        rotation_matrix = [[cos_theta, sin_theta], [-sin_theta, cos_theta]]

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
                    relative_tile_pos.x * rotation_matrix[1][0] + relative_tile_pos.y * rotation_matrix[1][1])
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
        upper_wall = self.entity_manager.create_entity("tiles/map_border_center", has_collider=True, is_static=True)
        upper_wall_transform = self.entity_manager.get_transform(upper_wall)
        upper_wall_transform.set_position(
            Vector2(self.type_map_list.get_width() * TILE_SIZE / 2, -TILE_SIZE + border_width))
        self.entity_manager.set_layer(upper_wall, RenderLayer.TILES)
        self.entity_manager.get_collider(upper_wall).debug_config_show_collider()

        bottom_wall = self.entity_manager.create_entity("tiles/map_border_center", has_collider=True, is_static=True)
        bottom_wall_transform = self.entity_manager.get_transform(bottom_wall)
        bottom_wall_transform.set_position(
            Vector2(self.type_map_list.get_width() * TILE_SIZE / 2, self.height - border_width))
        bottom_wall_transform.rotate(180)
        self.entity_manager.set_layer(bottom_wall, RenderLayer.TILES)
        self.entity_manager.get_collider(bottom_wall).debug_config_show_collider()

        left_wall = self.entity_manager.create_entity("tiles/map_border_lateral", has_collider=True, is_static=True)
        left_wall_transform = self.entity_manager.get_transform(left_wall)
        left_wall_transform.set_position(Vector2(-TILE_SIZE + border_width, self.height / 2))
        self.entity_manager.set_layer(left_wall, RenderLayer.TILES)
        self.entity_manager.get_collider(left_wall).debug_config_show_collider()

        right_wall = self.entity_manager.create_entity("tiles/map_border_lateral", has_collider=True, is_static=True)
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
        last_checkpoint_index = len(self.checkpoints) - 1
        next_checkpoint_number = 0 if checkpoint == last_checkpoint_index else checkpoint + 1
        for tile in self.checkpoints:
            if tile.checkpoint_number == next_checkpoint_number:
                tile_transform = self.entity_manager.get_transform(tile.entity_ID)
                return tile_transform.get_position().x, tile_transform.get_position().y
        return float('inf'), float('inf')

