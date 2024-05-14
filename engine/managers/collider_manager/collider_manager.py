from engine.components.collider import Collider
from engine.entities.entity import Entity


class ColliderManager:
    def __init__(self):
        self.colliders: list[Collider] = []

    def update(self, entity: Entity, delta_time: float) -> None:
        if not isinstance(entity, Entity):
            raise ValueError("entity must be an instance of Entity")
        collider = entity.get_collider()

        collider.update_rect(entity.get_sprite_rect())

        if collider not in self.colliders:
            self.colliders.append(collider)

        if entity.is_static():
            return  # Static entities don't move, so they don't need to check for collision
        self.check_collision_continuous(entity)

    def check_collision(self, entity: Entity) -> None:
        if not isinstance(entity, Entity):
            raise ValueError("entity must be an instance of Entity")

        collider = entity.get_collider()
        physics = entity.get_physics()
        transform = entity.get_transform()

        for other_collider in self.colliders:
            if other_collider is collider:
                continue

            intersection = collider.intersects(other_collider)
            if intersection.get_intersects():
                # Reverse the direction of velocity as a simple response to collision
                # This assumes the entity should bounce back with the same speed it hit the collider
                # Modify this logic based on your game's needs, for example, by reducing speed on collision
                physics.set_velocity(-physics.get_velocity())

                physics.set_velocity(physics.get_velocity() * (1 - min(intersection.get_intersection_area() / 100, 1)))

                direction_of_movement = -1 if physics.get_velocity() < 0 else 1
                transform.displace(
                    transform.get_forward() * direction_of_movement * 5)  # Adjust the displacement as needed

                break

    def check_collision_continuous(self, entity: Entity) -> None:
        collider = entity.get_collider()
        physics = entity.get_physics()
        transform = entity.get_transform()

        for other_collider in self.colliders:
            if other_collider is collider:
                continue
            if other_collider.is_in_training and collider.is_in_training:
                continue

            intersection = collider.intersects(other_collider)
            if intersection.get_intersects():
                # Reverse the velocity as a simple response to collision
                physics.set_velocity(-physics.get_velocity())

                # Adjust the entity's position slightly in the opposite direction of its current velocity
                # This is to ensure it doesn't remain stuck within the collider
                direction_of_movement = -1 if physics.get_velocity() < 0 else 1

                # Calculate a small displacement away from the collider
                # This can be a fixed small value or based on the intersection area or entity's speed
                displacement_magnitude = min(abs(physics.get_velocity()),
                                             5)  # Example: min current speed or a small constant
                slight_displacement = direction_of_movement * transform.get_forward() * displacement_magnitude

                # Apply the displacement to move the entity slightly away from the collision
                transform.displace(slight_displacement)

                break  # Exit the loop after handling the collision
