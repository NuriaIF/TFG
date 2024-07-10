"""
This module contains the TileMap class.
"""

import numpy as np
from black import Optional
from numpy import ndarray
from pygame import Vector2, Rect

from src.engine.managers.entity_manager.entity_manager import EntityManager
from src.game.entities.tile import Tile
from src.game.map.checkpoints.checkpoint_direction import CheckpointDirection
from src.game.map.map_types_list import MapTypeList
from src.game.resource_manager.checkpoints_loader import CheckpointsLoader
from src.game.resource_manager.map_loader import MapLoader
from src.game.map.map_types import MapType, map_type_to_encoded_value
from src.game.map.map_types import map_type_to_file
from src.engine.math.geometry import point_in_polygon

TILE_SIZE = 16
MAP_WALL_DEPTH = 100


class TileMap:
    """
    This tile map holds the all the tiles of the map as entities.
    Entities store the position and the sprite of each tile. All the tiles will be batched and rendered for
    optimization.
    """
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager

        self.tiles: list[Tile] = []
        self.type_map_list: MapTypeList = MapLoader.load_map("road01")
        self.current_map_name = "road01"

        self.checkpoints: list[Tile] = []
        self.checkpoint_lines: list[Tile] = []
        self.distance_between_checkpoints = []

        self.height = 0
        self.width = 0

        self.positions = []
        self.tiles_fov = []
        self.ordered_tiles = []

    def load_map(self, map_name: str) -> None:
        """
        Load the map corresponding to the given name
        :param map_name: The name of the map
        """
        print("Loading map")
        self.current_map_name = map_name
        self.type_map_list = MapLoader.load_map(map_name)
        self.height = self.type_map_list.get_height() * TILE_SIZE
        self.width = self.type_map_list.get_width() * TILE_SIZE

    def get_width_number(self):
        """
        Get the width of the map in number of tiles
        :return: The width of the map
        """
        return self.type_map_list.get_width()

    def get_height_number(self):
        """
        Get the height of the map in number of tiles
        :return: The height of the map
        """
        return self.type_map_list.get_height()

    def clear(self):
        """
        Clear the tile map
        """
        self.tiles = []
        self.checkpoints = []
        self.checkpoint_lines = []
        self.distance_between_checkpoints = []

    def generate_tiles(self) -> None:
        """
        This generates all the tiles.
        It iterates over the map of tile types and creates one entity for each one.
        The entities are configured as static and batched for optimization.
        It also sets the checkpoints and the checkpoint lines.
        :return:
        """
        print("Generating tiles")
        checkpoints_info = CheckpointsLoader.read_checkpoints(self.current_map_name)
        checkpoints_dict = checkpoints_info[0]
        checkpoints_directions_dict = checkpoints_info[1]

        for i in range(len(self.type_map_list)):
            x_pos = (i % self.type_map_list.get_width()) * TILE_SIZE
            y_pos = (i // self.type_map_list.get_width()) * TILE_SIZE

            index_x_pos = i % self.type_map_list.get_width()
            index_y_pos = i // self.type_map_list.get_width()

            map_type = self.type_map_list[i]
            map_file = map_type_to_file(map_type)
            tile_entity = self.entity_manager.create_entity("tiles/" + map_file, batched=True)
            tile = Tile(tile_entity, map_type, i, map_type_to_encoded_value(map_type))
            if self.type_map_list[i] == MapType.TRACK:
                if checkpoints_dict.get((index_x_pos, index_y_pos)) is not None:
                    tile.set_as_checkpoint(checkpoints_dict.get((index_x_pos, index_y_pos)))
                    self.checkpoints.append(tile)
            # Set the tile's position
            self.entity_manager.get_transform(tile_entity).set_position(Vector2(x_pos, y_pos))

            self.tiles.append(tile)

        # order checkpoints
        self.checkpoints = sorted(self.checkpoints, key=lambda x: x.checkpoint_number)
        self.process_checkpoints(checkpoints_directions_dict)

    def get_tile_at_pos_vec(self, vec2: Vector2) -> Tile:
        """
        Get the tile at the position of the vector
        :param vec2: The position of the tile as a vector
        :return: The tile at the position
        """
        [index_x, index_y] = self.get_tile_index_from_pos_vec(vec2)
        return self.get_tile(index_x, index_y)

    def get_tile_at_pos(self, x: float, y: float) -> Tile:
        """
        Get the tile at the position
        :param x: The tile x position
        :param y: The tile y position
        :return: The tile at the position or None if the position is out of bounds
        """
        return self.get_tile(x // TILE_SIZE, y // TILE_SIZE)

    @staticmethod
    def get_tile_index_from_pos_vec(position: Vector2) -> [int, int]:
        """
        Get the index of the tile from the position of the vector
        :param position: The position of the tile
        :return: The index of the tile
        """
        return int(position.x // TILE_SIZE), int(position.y // TILE_SIZE) + 1

    @staticmethod
    def get_index_from_pos(x: int, y: int) -> [int, int]:
        """
        Get the index of the tile from the position
        :param x: The x position of the tile
        :param y: The y position of the tile
        :return: The index of the tile
        """
        return x // TILE_SIZE, y // TILE_SIZE

    def get_tiles_within_square(self, position: tuple[float, float], radius: float, vision_box: ndarray,
                                angle: float) -> tuple[list[Tile], list[float]]:
        """
        This method returns a list of times and their encoded values that are within the vision box of the entity.
        :param position: The position of the entity
        :param radius: The radius of the vision box
        :param vision_box: The vision box of the entity
        :param angle: The angle of the entity
        :return: A tuple with the list of tiles and their encoded values
        """
        tiles: list[Tile] = []
        radius_doubled = radius * 2
        tiles_size = round((radius_doubled * radius_doubled)) // TILE_SIZE
        pos_x, pos_y = position
        tile_size_half = TILE_SIZE / 2

        polygon_array = np.array(vision_box, dtype=np.float64)
        for i in range(-tiles_size, tiles_size):
            offset_x = pos_x + i * TILE_SIZE
            for j in range(-tiles_size, tiles_size):
                offset_y = pos_y + j * TILE_SIZE
                tile = self.get_tile_at_pos(int(offset_x), int(offset_y))
                if tile is not None:
                    tile_position = self.entity_manager.get_transform(tile.entity_ID).get_position()
                    tile_pos = np.array([tile_position.x + tile_size_half, tile_position.y])
                    if point_in_polygon(tile_pos, polygon_array):
                        tiles.append(tile)

        tiles_and_codes = self._rotate_tiles(tiles, angle, pos_x, pos_y)
        tiles = tiles_and_codes[0]
        codes = tiles_and_codes[1]
        tiles = tiles[:144]
        codes = codes[:144]
        return tiles, codes

    def get_tiles_of_rect(self, entity_pos: Vector2, rect: Rect) -> list[Tile]:
        """
        This method returns all the tiles that are within the rectangle of the entity.
        :param entity_pos: The position of the entity
        :param rect: The rectangle
        :return: The tiles of the rectangle
        """
        tiles: list[Tile] = []
        rect_width = Vector2(rect.topright).distance_to(rect.topleft)
        rect_height = Vector2(rect.bottomleft).distance_to(rect.topleft)
        top: int = int(entity_pos.y + rect_height)
        bottom: int = int(entity_pos.y - rect_height)
        left: int = int(entity_pos.x - rect_width)
        right: int = int(entity_pos.x + rect_width)
        for x in range(left, right, TILE_SIZE):
            for y in range(bottom, top, TILE_SIZE):
                tile = self.get_tile_at_pos(x + TILE_SIZE / 2, y + TILE_SIZE * 1.5)
                if tile is not None:
                    tiles.append(tile)
        return tiles

    def set_checkpoint_line(self, start_index: int,
                            offset_func: tuple[callable, callable],
                            checkpoint_number: int):
        """
        This method sets the checkpoint line of the checkpoint.
        It works by setting all the tiles in the line of length 8 to be a checkpoint line.
        :param start_index:
        :param offset_func:
        :param checkpoint_number:
        :return:
        """
        for j in range(-4, 5):
            index = offset_func[0](start_index, j)
            index2 = offset_func[1](start_index, j)
            if 0 <= index < len(self.tiles):
                self.tiles[index].set_as_checkpoint(checkpoint_number)
                self.tiles[index2].set_as_checkpoint(checkpoint_number)
                self.checkpoint_lines.append(self.tiles[index])
                self.checkpoint_lines.append(self.tiles[index2])

    def get_offset_func(self, direction: CheckpointDirection):
        """
        This method returns the offset functions for the direction of the checkpoint.
        It returns the function that calculates the index of the tile in the line and the function that calculates the
        index of the next tile in the line.
        :param direction: The direction of the checkpoint
        :return: The offset functions
        """
        width = self.type_map_list.get_width()
        if direction == CheckpointDirection.HORIZONTAL:
            return lambda idx, j: idx + j, lambda idx, j: idx + j - width
        elif direction == CheckpointDirection.VERTICAL:
            return lambda idx, j: idx + j * width, lambda idx, j: idx + j * width + 1
        elif direction == CheckpointDirection.DIAGONAL_LEFT:
            return lambda idx, j: idx + j * width + j, lambda idx, j: idx + j * width + j + 1
        elif direction == CheckpointDirection.DIAGONAL_RIGHT:
            return lambda idx, j: idx + j * width - j, lambda idx, j: idx + j * width - j + 1
        else:
            raise ValueError(f"Unknown direction: {direction}")

    def process_checkpoints(self, checkpoints_directions_dict: dict[int, CheckpointDirection]) -> None:
        """
        This method processes the checkpoints and sets the checkpoint lines.
        It calculates the distance between the checkpoints.
        :param checkpoints_directions_dict: The dictionary of the directions of the checkpoints
        :return: None
        """
        for tile in self.checkpoints:
            direction = checkpoints_directions_dict[tile.checkpoint_number]
            offset_func = self.get_offset_func(direction)
            self.set_checkpoint_line(tile.index_in_map, offset_func, tile.checkpoint_number)

            distance = Vector2(self.get_next_checkpoint_position(tile.checkpoint_number)).distance_to(
                self.entity_manager.get_transform(tile.entity_ID).get_position())
            self.distance_between_checkpoints.append(distance)

    def get_tile(self, x, y):
        """
        Get the tile at the position
        :param x: The x position
        :param y: The y position
        :return: The tile at the position or None if the position is out of bounds
        """
        map_width = self.type_map_list.get_width()
        map_height = self.type_map_list.get_height()
        if 0 <= x < map_width and 0 <= y < map_height:
            return self.tiles[y * map_width + x]
        return None

    def _rotate_tiles(self, tiles: list[Tile], angle: float, position_x, position_y) -> tuple[list[Tile], list[float]]:
        """
        This method rotates the tiles by the angle.
        This is needed to calculate the field of view of the entity with its rotation.
        This works by rotating the tile positions and then sorting them by y and x.
        Will return the ordered tiles and their encoded values.
        :param tiles: The tiles to rotate
        :param angle: The angle of the entity
        :param position_x: The position of the entity
        :param position_y: The position of the entity
        :return: A tuple with the ordered tiles and their encoded values
        """
        theta = np.radians(angle)

        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)

        rotation_matrix = [[cos_theta, sin_theta], [-sin_theta, cos_theta]]

        ordered_tiles = []
        encoded_values = []
        position_and_tile_list = []

        self.positions = []

        for tile in tiles:
            if tile is not None:
                transform = self.entity_manager.get_transform(tile.entity_ID)
                tile_pos: Vector2 = transform.get_position()
                relative_tile_pos = (position_x - tile_pos.x, position_y - tile_pos.y)
                new_pos = np.dot(rotation_matrix, relative_tile_pos)
                new_x, new_y = new_pos[0], new_pos[1]
                rotated_tile_pos = (new_x, new_y)
                position_and_tile_list.append((rotated_tile_pos, tile))

        # Sort the list by y
        position_and_tile_list.sort(key=lambda item: item[0][1], reverse=True)

        # Group the list in several sublist of 12 elements
        grouped_arrays = [position_and_tile_list[i:i + 12] for i in range(0, len(position_and_tile_list), 12)]

        # Sort each sublist by x
        for sublist in grouped_arrays:
            sublist.sort(key=lambda item: item[0][0])
            ordered_tiles.extend([tile for _, tile in sublist])
            encoded_values.extend([tile.get_encoded_value() for _, tile in sublist])
            self.positions.extend([pos for pos, _ in sublist])

        return ordered_tiles, encoded_values

    def get_next_checkpoint_position(self, checkpoint: int) -> tuple[float, float]:
        """
        This method returns the position of the next checkpoint.
        This is needed to calculate the distance between the car and the next checkpoint.
        :param checkpoint: The current checkpoint
        :return: The position of the next checkpoint
        """
        last_checkpoint_index = len(self.checkpoints) - 1
        next_checkpoint_number = 0 if checkpoint == last_checkpoint_index else checkpoint + 1
        checkpoint_next = self.checkpoints[next_checkpoint_number]
        tile_transform = self.entity_manager.get_transform(checkpoint_next.entity_ID)
        return tile_transform.get_position().x, tile_transform.get_position().y
