"""
This module contains the SpriteLoader class.
"""
import pygame

GLOBAL_SPRITE_PATH = "assets/sprites/"
SPRITE_EXTENSION = ".png"


class SpriteLoader:
    """
    A class to load sprites from the disk and return them as a pygame.Surface.
    """
    @staticmethod
    def load(path: str) -> pygame.Surface:
        """
        Load a sprite from the disk and return it as a pygame.Surface.
        :param path: The path to the sprite to load
        :return: The sprite as a pygame.Surface
        """
        return pygame.image.load(GLOBAL_SPRITE_PATH + path + SPRITE_EXTENSION).convert_alpha()
