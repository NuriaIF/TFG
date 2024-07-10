"""
This module contains the BackgroundBatch class.
"""
import pygame
from pygame import Surface

from src.engine.components.transform import Transform


class BackgroundBatch:
    """
    This is a wrapper around a surface that contains all the sprites of the entities in the game.

    This is used to optimize the rendering of the background sprites.

    This takes all the sprites and transforms for a batch and creates a surface with all the sprites in the correct
    positions.
    """

    def __init__(self, entity_width: int, entity_height: int, sprites: list[Surface],
                 transforms: list[Transform]) -> None:
        """
        Initialize the background batch.
        This takes the width and height of the entities, the sprites and the transforms of the entities.
        Then it calculates the number of rows and columns needed to fit all the entities and creates a surface with
        all the sprites in the correct positions.
        :param entity_width: The width of the entities in pixels
        :param entity_height: The height of the entities in pixels
        :param sprites: The sprites of the entities
        :param transforms: The transforms of the entities
        """
        self.entity_width = entity_width
        self.entity_height = entity_height

        # Calculate the number of rows and columns
        min_x, max_x = float('inf'), float('-inf')
        min_y, max_y = float('inf'), float('-inf')

        for transform in transforms:
            pos = transform.get_position()
            if pos.x < min_x:
                min_x = pos.x
            if pos.x > max_x:
                max_x = pos.x
            if pos.y < min_y:
                min_y = pos.y
            if pos.y > max_y:
                max_y = pos.y

        self.cols = int((max_x - min_x) / entity_width) + 1
        self.rows = int((max_y - min_y) / entity_height) + 1

        self.batch_surface = pygame.Surface((self.cols * entity_width, self.rows * entity_height), pygame.SRCALPHA)
        self.batch_surface.fill((0, 0, 0, 0))  # Make the surface transparent

        # Offset to adjust positions relative to the origin
        self.offset_x = min_x
        self.offset_y = min_y

        # Add all tiles to the batch surface
        for sprite, transform in zip(sprites, transforms):
            self.add_entity(sprite, transform.get_position())

    def add_entity(self, sprite: Surface, position: pygame.Vector2) -> None:
        """
        Add an entity to the batch surface to be batched on the surface batch.
        :param sprite: The surface sprite of the entity
        :param position: The position of the entity
        :return: None
        """
        x = int((position.x - self.offset_x))
        y = int((position.y - self.offset_y))
        self.batch_surface.blit(sprite, (x, -y + self.rows * self.entity_height - 1))

    def get_batch_surface(self):
        """
        Get the batch surface.
        :return:
        """
        return self.batch_surface

    def get_width(self):
        """
        Get the width of the batch surface.
        :return:
        """
        return self.cols * self.entity_width

    def get_height(self):
        """
        Get the height of the batch surface.
        :return:
        """
        return self.rows * self.entity_height
