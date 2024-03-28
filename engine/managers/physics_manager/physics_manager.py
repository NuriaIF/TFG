from engine.components.collider import Collider
from engine.entities.entity import Entity


class PhysicsManager:
    def __init__(self):
        self.colliders: list[Collider] = []

    def update(self, entity: Entity, delta_time: float):
        physics = entity.get_physics()
        transform = entity.get_transform()

        # Apply drag to velocity. Drag should slow down the car, acting in the opposite direction.
        # Assuming drag is a positive scalar that needs to be subtracted from velocity.
        if physics.get_velocity() > 0:
            velocity_after_drag = physics.get_velocity() - (physics.get_drag() * physics.get_velocity())
            # Ensure velocity doesn't flip direction due to drag alone.
            physics.set_velocity(max(0.0, velocity_after_drag))
        elif physics.get_velocity() < 0:
            velocity_after_drag = physics.get_velocity() + (
                    physics.get_drag() * abs(physics.get_velocity()))
            # Ensure velocity doesn't flip direction due to drag alone.
            physics.set_velocity(min(0.0, velocity_after_drag))

        # Update acceleration based on force and mass.
        acceleration = physics.get_force() / physics.get_mass()

        # Update velocity with acceleration.
        physics.add_velocity(acceleration)

        displacement = physics.get_velocity() * delta_time
        transform.displace(transform.get_forward() * displacement)
        physics.set_force(0)

