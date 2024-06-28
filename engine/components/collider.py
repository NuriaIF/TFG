from typing import Optional, Callable

import pygame as pygame

from engine.components.physics import Physics
from engine.components.transform import Transform


class Intersection:
    def __init__(self, intersects: bool, intersection_area: float):
        self.intersects: bool = intersects
        self.intersection_area: float = intersection_area

    def get_intersects(self) -> bool:
        return self.intersects

    def get_intersection_area(self) -> float:
        return self.intersection_area


class Collider:
    def __init__(self, rect: pygame.Rect, is_active: bool = True):
        # if rect is None:
        #     raise ValueError("Rect cannot be None")
        # if not isinstance(rect, pygame.Rect):
        #     raise ValueError("Rect must be an instance of pygame.Rect")
        self.rect = rect
        self._is_active: bool = is_active
        self._collider_debug_show: bool = False
        self._colliding: bool = False

        self._non_collideable_colliders: set['Collider'] = set()
        self._collision_callback: Optional[Callable] = None

        self._collidered_physics: Physics | None = None
        self._collidered_transforms: Transform | None = None
        self._collidered_collider: Collider | None = None

    def set_collidered(self, physics: 'Physics | None', transform: 'Transform | None',
                       collider: 'Collider | None') -> None:
        self._collidered_physics = physics
        self._collidered_transforms = transform
        self._collidered_collider = collider

    def get_collidered_physics(self) -> Physics | None:
        return self._collidered_physics

    def get_collidered_collider(self) -> 'Collider | None':
        return self._collidered_collider

    def get_collidered_transform(self) -> Transform | None:
        return self._collidered_transforms

    def get_non_collideable_colliders(self) -> set['Collider']:
        return self._non_collideable_colliders

    def set_collision_callback(self, callback: Callable) -> None:
        self._collision_callback = callback

    def get_collision_callback(self) -> Optional[Callable]:
        return self._collision_callback

    def add_non_collideable_collider(self, collider: 'Collider') -> None:
        self._non_collideable_colliders.add(collider)

    def get_rect(self) -> pygame.Rect:
        return self.rect

    def update_rect(self, sprite_rect: pygame.Rect) -> None:
        # if rect is None:
        #     raise ValueError("Rect cannot be None")
        # if not isinstance(rect, pygame.Rect):
        #     raise ValueError("Rect must be an instance of pygame.Rect")
        self.rect = sprite_rect

    def intersects(self, other_collider: 'Collider') -> Intersection:
        """
        Returns a tuple with a boolean value and a float value. The boolean value is True if the collider intersects.
        The float is the area of the intersection. If the boolean value is False, the float value is 0.
        """
        # if not isinstance(other_collider, Collider):
        #     raise ValueError("other_collider must be an instance of Collider")

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


    def set_active(self, is_active: bool) -> None:
        self._is_active = is_active

    def set_colliding(self, colliding: bool) -> None:
        self._colliding = colliding

    def is_colliding(self) -> bool:
        return self._colliding

    def shows_debug_collider(self) -> bool:
        return self._collider_debug_show

    def debug_config_show_collider(self) -> None:
        self._collider_debug_show = True

    def debug_config_hide_collider(self) -> None:
        self._collider_debug_show = False

    def reset(self) -> None:
        self._collider_debug_show = False

        self.set_colliding(False)
        self.set_collidered(None, None, None)
