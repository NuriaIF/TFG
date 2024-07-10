"""
This module contains the Camera class, which encapsulates the behavior of the camera in the game.
"""
from pygame import Vector2

from src.game.camera_coordinates import CameraCoords


class Camera:
    """
    This class encapsulates the behavior of the camera in the game.
    Is just a simple class that keeps track of the position of the camera.
    Also, includes displacement behaviour for smooth movement.
    """
    def __init__(self):
        self._delta_time: float = 0

        self._position: Vector2 = Vector2(0, 0)
        self._previous_position: Vector2 = self._position
        self._displacement: Vector2 = Vector2(0, 0)
        self._moving: bool = False

    def set_position(self, position: Vector2) -> None:
        """
        Set the position of the camera.
        :param position: The new position of the camera
        :return: None
        """
        self._previous_position = self._position
        self._position = position
        CameraCoords.update_camera_position(self._position)

    def reset_position(self) -> None:
        """
        Reset the position of the camera.
        It also resets the previous position and the displacement.
        :return:
        """
        self._delta_time: float = 0
        self._position: Vector2 = Vector2(0, 0)
        self._previous_position: Vector2 = self._position
        self._displacement: Vector2 = Vector2(0, 0)
        self._moving: bool = False
        CameraCoords.update_camera_position(self._position)

    def update(self, delta_time: float) -> None:
        """
        Updates the position, applying the displacement.
        :param delta_time:
        :return:
        """
        self._delta_time = delta_time

        # Calculate displacement based on the change in position
        self._displacement = self._position - self._previous_position
        if self._displacement.length() > 0.01:  # Check if there's any displacement
            self._previous_position = self._position

    def move(self, displacement: Vector2) -> None:
        """
        Move the camera by a displacement.
        :param displacement: The displacement to move the camera
        :return: None
        """
        self.set_position(self._position + displacement * self._delta_time)

    @staticmethod
    def get_position() -> Vector2:
        """
        Get the position of the camera.
        :return:
        """
        return CameraCoords.get_camera_position()
