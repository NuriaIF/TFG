"""
This module contains the RenderLayer enum class for the different render layers.
"""
from enum import Enum


class RenderLayer(Enum):
    """
    Enum for the different render layers.
    """
    TILES = 10
    TILE_DEBUG = 11
    ENTITIES = 20
    SMOKE = 21
    ENTITIES_DEBUG = 21
    UI = 100
    DEFAULT = 1000
