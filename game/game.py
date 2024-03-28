import pygame
from pygame import Vector2

from engine.engine import Engine
from engine.managers.input_manager.key import Key
from game.car import Car
from game.map.tile_map import TileMap


class Game(Engine):
    def __init__(self):
        super().__init__()
        self.play_music("GameMusic")
        self.car = Car(self.create_entity("entities/car", has_collider=True, is_static=False))
        self.tile_map = TileMap(self)
        self.car.set_position(Vector2(400, 300))

    def update(self, delta_time):
        super().update(delta_time)
        self.car.update_input(self.input_manager)
        self.car.update(delta_time)
        self.move_camera()

        car_pos = self.car.car_entity.get_transform().get_position() + self.camera.get_position()
        closest_tile = self.tile_map.get_closest_tile((self.camera.get_position().x, self.camera.get_position().y))
        print(closest_tile.get_transform().get_position())
        # draw a rect on the stepped tile
        self.renderer.draw_rect(closest_tile.get_sprite_rect(), (255, 0, 0), 3)

    def move_camera(self):
        if self.input_manager.is_key_down(Key.K_UP):
            self.camera.move(Vector2(0, 100))
        if self.input_manager.is_key_down(Key.K_DOWN):
            self.camera.move(Vector2(0, -100))
        if self.input_manager.is_key_down(Key.K_LEFT):
            self.camera.move(Vector2(-100, 0))
        if self.input_manager.is_key_down(Key.K_RIGHT):
            self.camera.move(Vector2(100, 0))

        """ 
        The camera follows the car, if the car leaves a box centered on the camera, the camera moves to the car's 
        position
        """
        self.center_camera_on_car()

    def center_camera_on_car(self):
        car_position = self.car.car_entity.get_transform().get_position()
        camera_position = -self.camera.get_position() + Vector2(self.window.get_width(), self.window.get_height())
        difference = camera_position - car_position
        if difference.length() > 1:
            self.camera.move(difference)

    def follow_player(self):
        # Define the "box" dimensions within which the camera doesn't need to move
        camera_box_width = self.window.get_width() / 5
        camera_box_height = self.window.get_height() / 5

        # Calculate the distance from the car to the camera
        distance_to_box = self.car.car_entity.get_transform().get_position() - self.camera.get_position()

        # Check if the car is outside the "box" area
        if abs(distance_to_box.x) > camera_box_width or abs(distance_to_box.y) > camera_box_height:
            # Move the camera by the distance needed to re-center the car
            self.camera.move(-distance_to_box)
