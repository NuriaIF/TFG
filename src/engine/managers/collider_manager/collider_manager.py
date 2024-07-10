"""
This module contains the ColliderManager class.
"""
from src.engine.components.collider import Collider
from src.engine.components.physics import Physics
from src.engine.components.transform import Transform

from src.engine.managers.entity_manager.entity_manager import EntityManager
from src.engine.managers.render_manager.renderer import DebugRenderer


class ColliderManager:
    """
    The collision manager is responsible for checking for collisions between colliders and to report the collision
    information. It also renders the colliders for debugging purposes.
    """
    def __init__(self, entity_manager: EntityManager, debug_renderer: DebugRenderer):
        self._debug_renderer = debug_renderer
        self._entity_manager = entity_manager
        self._entities_with_colliders = []

    def send_data(self, entity: int) -> None:
        """
        Add an entity to the list of entities with colliders.
        This is useful as not all entities have colliders, so we only need to check for collisions between entities
        This optimizes the collision checking process a lot.
        :param entity:
        :return: None
        """
        self._entities_with_colliders.append(entity)

    def debug_render(self) -> None:
        """
        Render the colliders for debugging purposes.
        :return: None
        """
        for entity in self._entities_with_colliders:
            collider: Collider = self._entity_manager.get_collider(entity)
            self._debug_renderer.draw_rect_absolute(collider.get_rect())

    def update(self) -> None:
        """
        Update the collision manager.
        The update is in charge of checking for collisions between colliders.
        :return:
        """
        colliders: list[Collider] = []
        for entity in self._entities_with_colliders:
            physics: Physics = self._entity_manager.get_physics(entity)
            if physics.is_static():
                return  # Static entities don't move, so they don't need to check for collision
            colliders.append(self._entity_manager.get_collider(entity))
            collider: Collider = self._entity_manager.get_collider(entity)
            transform: Transform = self._entity_manager.get_transform(entity)
            self._check_collision(collider, physics, transform)

    def _check_collision(self, collider: Collider, physics: Physics, transform: Transform) -> None:
        """
        Check for collisions between the given collider and all the other colliders.
        This method is called for each collider in the list of entities with colliders in the update method.
        If a collision is detected, the velocity of the collider is set to be the opposite of the direction from one
        transform to the other. The callback of the collider is also called if it exists.
        :param collider: The collider to check for collisions
        :param physics: The physics component of the entity
        :param transform: The transform component of the entity
        :return: None
        """
        colliding = False
        for entity in self._entities_with_colliders:
            other_collider: Collider = self._entity_manager.get_collider(entity)
            other_transform: Transform = self._entity_manager.get_transform(entity)
            other_physics: Physics = self._entity_manager.get_physics(entity)

            if other_collider is collider:
                continue

            # This reiterative (collider.is_active()) check is necessary because the callback may have
            # changed the collider active state
            if not other_collider.is_active() or not collider.is_active():
                continue

            if other_collider in collider.get_non_collideable_colliders():
                continue

            intersection = collider.intersects(other_collider)
            if intersection.get_intersects():
                colliding = True
                # Set the velocity to be the opposite of the direction from one transform to the other
                colliders_direction = transform.get_position() - other_transform.get_position()
                collider.set_collidered(other_physics, other_transform, other_collider)
                physics.set_vector_velocity(colliders_direction.normalize() * 100000 / physics.get_mass())
                if collider.get_collision_callback() is not None:
                    collider.get_collision_callback()()
            collider.set_colliding(colliding)

    def clear(self) -> None:
        """
        Clear the collision manager.
        :return: None
        """
        self._entities_with_colliders.clear()

