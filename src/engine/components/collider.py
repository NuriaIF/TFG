"""
The Collider class is responsible for storing the rectangle that represents the collision box of an entity.
"""
from typing import Optional, Callable

import pygame as pygame

from src.engine.components.physics import Physics
from src.engine.components.transform import Transform


class Intersection:
    """
    A class representing the intersection between two colliders. It contains a boolean value that indicates if the
    colliders intersect and a float value that represents the area of the intersection.

    This class is meant to be used as an information container for the Collider class.
    """

    def __init__(self, intersects: bool, intersection_area: float):
        self.intersects: bool = intersects
        self.intersection_area: float = intersection_area

    def get_intersects(self) -> bool:
        """
        Get the boolean value that indicates if the colliders intersect.
        :return: True if the colliders intersect, False otherwise
        """
        return self.intersects

    def get_intersection_area(self) -> float:
        """
        Get the area of the intersection between the colliders.
        """
        return self.intersection_area


class Collider:
    """
    The Collider class is responsible for storing the rectangle that represents the collision box of an entity.
    It is also responsible for checking if it intersects with another collider and for storing information about
    the collisions.
    """

    def __init__(self, rect: pygame.Rect, is_active: bool = True):
        # if rect is None:
        #     raise ValueError("Rect cannot be None")
        # if not isinstance(rect, pygame.Rect):
        #     raise ValueError("Rect must be an instance of pygame.Rect")
        self.rect = rect
        self._is_active: bool = is_active
        self._collider_debug_show: bool = False
        self._colliding: bool = False

        self._non_collideable_colliders: set[Collider] = set()
        self._collision_callback: Optional[Callable] = None

        self._collidered_physics: Optional[Physics] = None
        self._collidered_transforms: Optional[Transform] = None
        self._collidered_collider: Optional[Collider] = None

    def set_collidered(self, physics: 'Physics | None', transform: 'Transform | None',
                       collider: 'Collider | None') -> None:
        """
        Set the physics, transform and collider of the entity that is being collided with.
        This is useful for collision callbacks and for actions that need to be taken when a collision occurs.
        :param physics: The physics of the entity that is being collided with
        :param transform: The transform of the entity that is being collided with
        :param collider: The collider of the entity that is being collided with
        :return: None
        """
        self._collidered_physics = physics
        self._collidered_transforms = transform
        self._collidered_collider = collider

    def get_collidered_physics(self) -> Optional[Physics]:
        """
        Get the physics of the entity that is being collided with.
        :return: The physics of the entity that is being collided with if it exists, None otherwise
        """
        return self._collidered_physics

    def get_collidered_collider(self) -> Optional['Collider']:
        """
        Get the collider of the entity that is being collided with.
        :return: The collider of the entity that is being collided with if it exists, None otherwise
        """
        return self._collidered_collider

    def get_collidered_transform(self) -> Optional[Transform]:
        """
        Get the transform of the entity that is being collided with.
        :return: The transform of the entity that is being collided with if it exists, None otherwise
        """
        return self._collidered_transforms

    def get_non_collideable_colliders(self) -> set['Collider']:
        """
        Get the set of colliders that this collider should not collide with.
        If a collider is in this set, it will not be checked for collision.
        :return:
        """
        return self._non_collideable_colliders

    def set_collision_callback(self, callback: Callable) -> None:
        """
        Set the collision callback function.
        This function will be called when a collision occurs.
        :param callback: The callback function
        :return: None
        """
        self._collision_callback = callback

    def get_collision_callback(self) -> Optional[Callable]:
        """
        Get the collision callback function.
        :return:
        """
        return self._collision_callback

    def add_non_collideable_collider(self, collider: 'Collider') -> None:
        """
        Add a collider to the set of colliders that this collider should not collide with.
        :param collider: The collider to add
        :return: None
        """
        self._non_collideable_colliders.add(collider)

    def get_rect(self) -> pygame.Rect:
        """
        Get the rect of the collider.
        :return: The rect of the collider
        """
        return self.rect

    def update_rect(self, sprite_rect: pygame.Rect) -> None:
        """
        Update the rect of the collider, directly setting it to the given rect.
        :param sprite_rect: The new rect of the collider
        :return: None
        """
        # if rect is None:
        #     raise ValueError("Rect cannot be None")
        # if not isinstance(rect, pygame.Rect):
        #     raise ValueError("Rect must be an instance of pygame.Rect")
        self.rect = sprite_rect

    def intersects(self, other_collider: 'Collider') -> Intersection:
        """
        Returns a tuple with a boolean value and a float value. The boolean value is True if the collider intersects.
        The float is the area of the intersection. If the boolean value is False, the float value is 0.
        :param other_collider: The other collider to check for intersection
        :return: A class Intersection with the intersection information.
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
        """
        Check if the collider is active.
        If the collider is not active, it will not be checked for collision.
        :return:
        """
        return self._is_active

    def set_active(self, is_active: bool) -> None:
        """
        Set the collider as active or inactive.
        If the collider is not active, it will not be checked for collision.
        :param is_active: True if the collider is active, False otherwise
        :return: None
        """
        self._is_active = is_active

    def set_colliding(self, colliding: bool) -> None:
        """
        Set the colliding state of the collider.
        :param colliding:
        :return:
        """
        self._colliding = colliding

    def is_colliding(self) -> bool:
        """
        Check if the collider is colliding with another collider.
        :return:
        """
        return self._colliding

    def shows_debug_collider(self) -> bool:
        """
        Returns whether the collider should be shown in debug mode.
        :return:
        """
        return self._collider_debug_show

    def debug_config_show_collider(self) -> None:
        """
        Sets the collider to be shown in debug mode.
        :return:
        """
        self._collider_debug_show = True

    def debug_config_hide_collider(self) -> None:
        """
        Sets the collider to be hidden in debug mode.
        :return:
        """
        self._collider_debug_show = False

    def reset(self) -> None:
        """
        Totally resets the collider.
        :return:
        """
        self._collider_debug_show = False

        self.set_colliding(False)
        self.set_collidered(None, None, None)
