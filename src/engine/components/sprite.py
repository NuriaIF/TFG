import pygame
from pygame import Vector2

from src.engine.components.transform import Transform
from src.engine.managers.resource_manager.sprite_loader import SpriteLoader
from src.game.camera_coordinates import apply_view_to_pos_vec


class Sprite(pygame.sprite.Sprite):
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
        """Update transform parameters and mark sprite as dirty."""
        if transform is None:
            raise ValueError("Transform cannot be None")
        # check if transform has changed
        self.transform = transform
        self.dirty = True
        self.camera_pos: Vector2 = camera_pos

    def update(self, *args):
        """Apply transformations if sprite is dirty."""
        if self.dirty:
            self.apply_transform()
            self.dirty = False

    def apply_transform(self):
        """Apply stored transformations to the sprite."""
        # And then rotate the scaled image in two steps, instead of using rotozoom
        self.image = pygame.transform.rotate(self.original_image, self.transform.get_rotation() + 180)
        pos_view_space: Vector2 = self.transform.get_position().copy()
        apply_view_to_pos_vec(pos_view_space, self.camera_pos)
        self.rect = self.image.get_rect(center=pos_view_space)

    def is_added_to_renderer(self) -> bool:
        return self._is_added_to_renderer

    def set_added_to_renderer(self) -> None:
        self._is_added_to_renderer = True

    def get_rect(self) -> pygame.Rect:
        return self.rect

    def get_width(self) -> int:
        return self.rect.width

    def get_height(self) -> int:
        return self.rect.height
