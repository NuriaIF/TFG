from typing import Dict, Tuple

from pygame import Vector2

from engine.managers.resource_manager.file_loader import FileLoader
from game.map.checkpoints.checkpoint_direction import CheckpointDirection

GLOBAL_CHECKPOINTS_PATH = "assets/tracks/"
CHECKPOINTS_EXTENSION = ".checkpoints"


class CheckpointsLoader:
    @staticmethod
    def read_checkpoints(map_name) -> tuple[dict[tuple[int, int]], dict[int]]:
        checkpoints_dict: dict[tuple[int, int]] = {}
        checkpoints_directions: dict[int] = {}
        checkpoints_path = GLOBAL_CHECKPOINTS_PATH + map_name + CHECKPOINTS_EXTENSION
        text_checkpoints = FileLoader.load(checkpoints_path)
        index = 0
        for line in text_checkpoints.split("\n"):
            parts = line.strip().split(", ")
            if len(parts) == 4:
                checkpoints_dict[(int(parts[1]), int(parts[2]))] = index
                checkpoints_directions[index] = (
                    CheckpointsLoader.convert_character_to_direction(parts[3]))
                index += 1
        return checkpoints_dict, checkpoints_directions

    @staticmethod
    def convert_character_to_direction(character: str) -> CheckpointDirection:
        if character == "-":
            return CheckpointDirection.HORIZONTAL
        elif character == "|":
            return CheckpointDirection.VERTICAL
        elif character == "\\":
            return CheckpointDirection.DIAGONAL_LEFT
        elif character == "/":
            return CheckpointDirection.DIAGONAL_RIGHT
