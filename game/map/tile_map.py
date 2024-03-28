from pygame import Vector2

from engine.engine import Engine
from engine.entities.entity import Entity
from engine.managers.render_manager.render_layers import RenderLayer
from game.map.map_loader import MapLoader
from game.map.map_types import MapType

TILE_SIZE = 16
MAP_WALL_DEPTH = 100


class TileMap:
    def __init__(self, engine: Engine):
        # Map position -> tile
        self.tiles: dict[tuple[int, int], Entity] = {}
        self.type_map_list = MapLoader.load_map("road01-uni")
        self.generate_tiles(engine)
        self.lateral_height = self.type_map_list.get_height() * TILE_SIZE
        self.vertical_width = self.type_map_list.get_width() * TILE_SIZE
        self.generate_walls(engine)

    def generate_tiles(self, engine: Engine) -> None:
        for i in range(len(self.type_map_list)):
            x_pos = (i % self.type_map_list.get_width()) * TILE_SIZE
            y_pos = (i // self.type_map_list.get_width()) * TILE_SIZE

            if self.type_map_list[i] == MapType.TRACK:
                tile_entity = engine.create_entity("tiles/track", background_batched=True, is_static=True)
            elif self.type_map_list[i] == MapType.GRASS:
                tile_entity = engine.create_entity("tiles/grass", background_batched=True, is_static=True)
            elif self.type_map_list[i] == MapType.SIDEWALK:
                tile_entity = engine.create_entity("tiles/sidewalk", background_batched=True, is_static=True)
            elif self.type_map_list[i] == MapType.FOREST:
                tile_entity = engine.create_entity("tiles/forest", background_batched=True, is_static=True)
            else:
                tile_entity = engine.create_entity("tiles/road_centre_line", background_batched=True, is_static=True)
                tile_entity.debug_config_show_collider()

            # Set the tile's position
            tile_entity.get_transform().set_position(Vector2(x_pos, y_pos))

            self.tiles[(x_pos, y_pos)] = tile_entity

    def get_closest_tile(self, position: tuple[int, int]) -> Entity:
        remaining = (position[0] % TILE_SIZE, position[1] % TILE_SIZE)
        closest_tile_pos = (position[0] - remaining[0], position[1] - remaining[1])
        return self.tiles[closest_tile_pos]

    def generate_walls(self, engine: Engine) -> None:
        # Create large entities that surround the map that have colliders, so the car can't leave the map
        upper_wall = engine.create_entity("tiles/map_border_center", has_collider=True, is_static=True)
        upper_wall.get_transform().set_position(Vector2(upper_wall.get_sprite_rect().width / 2 - TILE_SIZE, -TILE_SIZE))
        upper_wall.set_layer(RenderLayer.TILES)
        upper_wall.debug_config_show_collider()

        bottom_wall = engine.create_entity("tiles/map_border_center", has_collider=True, is_static=True)
        bottom_wall.get_transform().set_position(
            Vector2(self.type_map_list.get_width() * TILE_SIZE / 2, self.lateral_height))
        bottom_wall.get_transform().rotate(180)
        bottom_wall.set_layer(RenderLayer.TILES)
        bottom_wall.debug_config_show_collider()

        right_wall = engine.create_entity("tiles/map_border_lateral", has_collider=True, is_static=True)
        right_wall.get_transform().set_position(Vector2(-TILE_SIZE, self.lateral_height / 2))
        right_wall.set_layer(RenderLayer.TILES)
        right_wall.debug_config_show_collider()

        left_wall = engine.create_entity("tiles/map_border_lateral", has_collider=True, is_static=True)
        left_wall.get_transform().set_position(Vector2(self.vertical_width, self.lateral_height / 2))
        left_wall.get_transform().rotate(180)
        left_wall.set_layer(RenderLayer.TILES)
        left_wall.debug_config_show_collider()
