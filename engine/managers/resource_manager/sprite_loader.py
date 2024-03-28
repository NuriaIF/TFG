import pygame

GLOBAL_SPRITE_PATH = "assets/sprites/"
SPRITE_EXTENSION = ".png"


class SpriteLoader:
    @staticmethod
    def load(path: str):
        return pygame.image.load(GLOBAL_SPRITE_PATH + path + SPRITE_EXTENSION).convert_alpha()
