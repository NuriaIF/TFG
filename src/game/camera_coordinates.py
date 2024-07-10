"""
This module contains functions that are used to map the window coordinates to the game coordinates.
"""
import pygame
from pygame import Vector2


def apply_view_to_pos(x: int, y: int, view_x: int, view_y: int) -> tuple:
    """
    Apply the view to the position.
    This function maps the window coordinates to the game coordinates.
    It is very important as this will allow game coordinates and window coordinates to be different.
    :param x: The x coordinate of the position to be mapped
    :param y: The y coordinate of the position to be mapped
    :param view_x: The x coordinate of the view (camera)
    :param view_y: The y coordinate of the view (camera)
    :return: The new position
    """
    # Subtract the view coordinates and return the new position
    return x - view_x + CameraCoords.get_window_size().x / 2, - y + view_y + CameraCoords.get_window_size().y / 2


def apply_view_to_pos_vec(vec2: pygame.Vector2, view: pygame.Vector2) -> None:
    """
    This maps the window coordinates to the game coordinates using a Vector2.
    :param vec2:
    :param view:
    :return: None
    """
    vec2.update(apply_view_to_pos(vec2.x, vec2.y, view.x, view.y))


def apply_view_to_rect(rect: pygame.Rect, view: pygame.Vector2) -> None:
    """
    This maps the window coordinates of a rect to the game coordinates.
    :param rect:
    :param view:
    :return: None
    """
    view_top_left = apply_view_to_pos(rect.topleft[0], rect.topleft[1], view.x, view.y)
    rect.update(view_top_left[0], view_top_left[1], rect.width, rect.height)


class CameraCoords:
    """
    This class holds static variables that represent the camera position and the window size.
    """
    _static_camera_pos: Vector2 = Vector2(0, 0)
    _static_window_size: Vector2 = Vector2(0, 0)

    @staticmethod
    def update_window_size(window_size: Vector2) -> None:
        """
        Update the window size
        :param window_size: The new window size
        :return: None
        """
        CameraCoords._static_window_size = window_size

    @staticmethod
    def update_camera_position(position: Vector2) -> None:
        """
        Update the camera position
        :param position: The new camera position
        :return: None
        """
        CameraCoords._static_camera_pos = position

    @staticmethod
    def get_window_size() -> Vector2:
        """
        Get the window size
        :return: The window size Vector2
        """
        return CameraCoords._static_window_size

    @staticmethod
    def get_camera_position() -> Vector2:
        """
        Get the camera position
        :return: The camera position Vector2
        """
        return CameraCoords._static_camera_pos
