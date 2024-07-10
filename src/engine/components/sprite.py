"""
This module contains the Sprite class.
"""
import pygame
from pygame import Vector2

from src.engine.components.transform import Transform
from src.engine.managers.resource_manager.sprite_loader import SpriteLoader
from src.game.camera_coordinates import apply_view_to_pos_vec


class Sprite(pygame.sprite.Sprite):
    """
    A class representing a sprite that can be drawn on the screen. This sprite inherits from pygame.sprite.Sprite
    and contains a reference to the original image, a rect that fits the image and a transform that represents the
    position, rotation and scale of the sprite.

    The sprite needs to hold to a transform because of how layered sprite group optimizes the rendering. The group
    needs to update all the sprites and then render them, so the sprite needs to hold the transform and update it
    when needed.
    """
    def __init__(self, image_path: str):
        super().__init__()
        self.original_image = SpriteLoader.load(image_path)
        self.image = self.original_image
        self.rect = self.image.get_rect()
        # Initialize transformation parameters
        self.transform = Transform()
        self.dirty = True  # Mark sprite as needing an update
        self._is_added_to_renderer = False
        self.camera_pos: Vector2 = Vector2(0, 0)

    def update_transform(self, transform: Transform, camera_pos: Vector2) -> None:
        """
        Update transform parameters and mark sprite as dirty.
        :param transform: The new transform of the sprite
        :param camera_pos: The position of the camera
        :return: None
        """
        if transform is None:
            raise ValueError("Transform cannot be None")
        # check if transform has changed
        self.transform = transform
        self.dirty = True
        self.camera_pos: Vector2 = camera_pos

    def update(self, *args) -> None:
        """
        Apply transformations if sprite is dirty.
        :param args:
        :return: None
        """
        if self.dirty:
            self.apply_transform()
            self.dirty = False

    def apply_transform(self) -> None:
        """
        Apply stored transformations to the sprite.
        Applies rotations and scaling to the sprite (if any).
        :return: None
        """
        # And then rotate the scaled image in two steps, instead of using rotozoom
        self.image = pygame.transform.rotate(self.original_image, self.transform.get_rotation() + 180)
        pos_view_space: Vector2 = self.transform.get_position().copy()
        apply_view_to_pos_vec(pos_view_space, self.camera_pos)
        self.rect = self.image.get_rect(center=pos_view_space)

    def is_added_to_renderer(self) -> bool:
        """
        Check if the sprite has been added to the renderer.
        :return: True if the sprite has been added to the renderer, False otherwise
        """
        return self._is_added_to_renderer

    def set_added_to_renderer(self) -> None:
        """
        Set the sprite as added to the renderer.
        :return: None
        """
        self._is_added_to_renderer = True

    def get_rect(self) -> pygame.Rect:
        """
        Get the rect of the sprite.
        :return: The rect of the sprite
        """
        return self.rect

    def get_width(self) -> int:
        """
        Get the width of the sprite.
        :return: The width of the sprite
        """
        return self.rect.width

    def get_height(self) -> int:
        """
        Get the height of the sprite.
        :return: The height of the sprite
        """
        return self.rect.height
