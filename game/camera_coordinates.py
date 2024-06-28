import pygame
from pygame import Vector2


def apply_view_to_pos(x: int, y: int, view_x: int, view_y: int) -> tuple:
    # Subtract the view coordinates and return the new position
    return x - view_x + CameraCoords.get_window_size().x/2, - y + view_y + CameraCoords.get_window_size().y/2


def apply_view_to_pos_vec(vec2: pygame.Vector2, view: pygame.Vector2) -> None:
    vec2.update(apply_view_to_pos(vec2.x, vec2.y, view.x, view.y))

def apply_view_to_rect(rect: pygame.Rect, view: pygame.Vector2) -> None:
    view_top_left = apply_view_to_pos(rect.topleft[0], rect.topleft[1], view.x, view.y)
    rect.update(view_top_left[0], view_top_left[1], rect.width, rect.height)


class CameraCoords:
    _static_camera_pos: Vector2 = Vector2(0, 0)
    _static_window_size: Vector2 = Vector2(0, 0)

    @staticmethod
    def update_window_size(window_size: Vector2) -> None:
        CameraCoords._static_window_size = window_size

    @staticmethod
    def update_camera_position(position: Vector2) -> None:
        CameraCoords._static_camera_pos = position

    @staticmethod
    def get_window_size() -> Vector2:
        return CameraCoords._static_window_size

    @staticmethod
    def get_camera_position() -> Vector2:
        return CameraCoords._static_camera_pos
