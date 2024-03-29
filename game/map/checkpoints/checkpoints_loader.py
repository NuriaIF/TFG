from typing import Dict, Tuple

from pygame import Vector2

from engine.managers.resource_manager.file_loader import FileLoader

GLOBAL_CHECKPOINTS_PATH = "assets/tracks/"
CHECKPOINTS_EXTENSION = ".checkpoints"


class CheckpointsLoader:
    @staticmethod
    def read_checkpoints(map_name) -> dict[tuple[int, int]]:
        checkpoints_dict: dict[tuple[int, int]] = {}
        checkpoints_path = GLOBAL_CHECKPOINTS_PATH + map_name + CHECKPOINTS_EXTENSION
        text_checkpoints = FileLoader.load(checkpoints_path)
        for line in text_checkpoints.split("\n"):
            parts = line.strip().split(", ")
            if len(parts) == 4:
                checkpoint = Vector2(float(parts[1]), float(parts[2]))
                checkpoints_dict[(int(parts[1]), int(parts[2]))] = checkpoint
        return checkpoints_dict
