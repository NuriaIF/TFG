import pygame as pygame


class Intersection:
    def __init__(self, intersects: bool, intersection_area: float):
        self.intersects: bool = intersects
        self.intersection_area: float = intersection_area

    def get_intersects(self) -> bool:
        return self.intersects

    def get_intersection_area(self) -> float:
        return self.intersection_area


class Collider:
    def __init__(self, rect: pygame.Rect, is_active: bool = True, is_training: bool = False):
        if rect is None:
            raise ValueError("Rect cannot be None")
        if not isinstance(rect, pygame.Rect):
            raise ValueError("Rect must be an instance of pygame.Rect")
        self.rect = rect
        self._is_in_training: bool = is_training
        self._is_active: bool = is_active
        self._collider_debug_show: bool = False

    def get_rect(self) -> pygame.Rect:
        return self.rect

    def update_rect(self, rect: pygame.Rect) -> None:
        if rect is None:
            raise ValueError("Rect cannot be None")
        if not isinstance(rect, pygame.Rect):
            raise ValueError("Rect must be an instance of pygame.Rect")
        self.rect = rect

    def intersects(self, other_collider: 'Collider') -> Intersection:
        """
        Returns a tuple with a boolean value and a float value. The boolean value is True if the collider intersects.
        The float is the area of the intersection. If the boolean value is False, the float value is 0.
        """
        if not isinstance(other_collider, Collider):
            raise ValueError("other_collider must be an instance of Collider")

        # Check for intersection
        intersects = self.rect.colliderect(other_collider.get_rect())
        if intersects:
            # Calculate intersection rectangle
            intersection_rect = self.rect.clip(other_collider.get_rect())
            # Calculate area of intersection
            intersection_area = intersection_rect.width * intersection_rect.height
            return Intersection(True, intersection_area)
        else:
            return Intersection(False, 0.0)

    def is_active(self):
        return self._is_active

    def is_in_training(self):
        return self._is_in_training

    def set_active(self, is_active: bool) -> None:
        self._is_active = is_active

    def shows_debug_collider(self) -> bool:
        return self._collider_debug_show

    def debug_config_show_collider(self) -> None:
        self._collider_debug_show = True

    def debug_config_hide_collider(self) -> None:
        self._collider_debug_show = False
