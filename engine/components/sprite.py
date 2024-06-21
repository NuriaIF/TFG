import pygame

from engine.components.transform import Transform
from engine.managers.resource_manager.sprite_loader import SpriteLoader


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

    def update_transform(self, transform: Transform):
        """Update transform parameters and mark sprite as dirty."""
        if transform is None:
            raise ValueError("Transform cannot be None")
        # check if transform has changed
        self.transform = transform
        self.dirty = True

    def update(self, *args):
        """Apply transformations if sprite is dirty."""
        if self.dirty:
            self.apply_transform()
            self.dirty = False

    def apply_transform(self):
        """Apply stored transformations to the sprite."""
        original_rect = self.original_image.get_rect()
        # To be able to apply scale separately on x and y, we need to scale the image first
        scaled_size = (int(original_rect.width * self.transform.get_scale()[0]),
                       int(original_rect.height * self.transform.get_scale()[1]))
        scaled_image = pygame.transform.scale(self.original_image, scaled_size)

        # And then rotate the scaled image in two steps, instead of using rotozoom
        self.image = pygame.transform.rotate(scaled_image, -self.transform.get_rotation())
        self.rect = self.image.get_rect(center=self.transform.get_position())

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
