from engine.components.collider import Collider
from engine.components.physics import Physics
from engine.components.transform import Transform
from pygame import Rect

class ColliderManager:
    def __init__(self):
        self.colliders: list[Collider] = []

    def update(self, collider: Collider, sprite_rect: Rect, physics: Physics, transform: Transform,
               next_frame_collider: Collider) -> None:
        # if not isinstance(entity, Entity):
        #     raise ValueError("entity must be an instance of Entity")
        # if not isinstance(collider, Collider):
        #     raise ValueError("collider must be an instance of Collider")
        # if not isinstance(sprite_rect, Rect):
        #     raise ValueError("sprite_rect must be an instance of pygame.Rect")

        collider.update_rect(sprite_rect)

        if collider not in self.colliders:
            self.colliders.append(collider)

        if physics.is_static():
            return  # Static entities don't move, so they don't need to check for collision
        self.check_collision_continuous(collider, physics, transform, next_frame_collider)

    def check_collision_continuous(self, collider: Collider, physics: Physics, transform: Transform,
                                   next_frame_collider: Collider) -> None:
        colliding = False
        for other_collider in self.colliders:
            if other_collider is collider:
                continue
            if other_collider.is_in_training() and collider.is_in_training():
                continue

            intersection = collider.intersects(other_collider)
            if intersection.get_intersects():
                colliding = True
                # Reverse the velocity as a simple response to collision
                physics.set_velocity(-physics.get_velocity() * 0.05)

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

        collider.set_colliding(colliding)
