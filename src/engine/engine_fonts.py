"""
This module contains the EngineFonts class.
"""

import pygame

from src.engine.engine_attributes import EngineAttributes


class EngineFonts:
    """
    A class to hold the fonts used in the engine.
    This class is a singleton.
    """
    _instance: "EngineFonts" = None
    debug_UI_font: pygame.font.Font
    debug_entity_font: pygame.font.Font

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EngineFonts, cls).__new__(cls)
            cls._instance.debug_UI_font = pygame.font.SysFont(EngineAttributes.DEBUG_FONT,
                                                              EngineAttributes.DEBUG_UI_FONT_SIZE)
            cls._instance.debug_entity_font = pygame.font.SysFont(EngineAttributes.DEBUG_FONT,
                                                                  EngineAttributes.DEBUG_ENTITY_FONT_SIZE, bold=True)

    @classmethod
    def get_fonts(cls) -> "EngineFonts":
        """
        Get the instance of the EngineFonts class.
        :return: The instance of the EngineFonts class
        """
        return cls._instance
