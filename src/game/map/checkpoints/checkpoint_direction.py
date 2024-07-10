"""
This module contains the CheckpointDirection enum class.
"""
from enum import Enum


class CheckpointDirection(Enum):
    """
    Enum class for the direction of a checkpoint.
    When reading the map, the checkpoints can be in 4 directions
    This enum represents those directions
    """
    HORIZONTAL = 0
    VERTICAL = 1
    DIAGONAL_LEFT = 2
    DIAGONAL_RIGHT = 3
