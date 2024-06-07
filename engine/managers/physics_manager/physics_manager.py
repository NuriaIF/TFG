from engine.components.physics import Physics
from engine.components.transform import Transform
from engine.entities.entity import Entity


def update_physics_and_transform(physics: Physics, transform: Transform, delta_time: float) -> (Transform, Physics):
    # Apply drag to velocity. Drag should slow down the car, acting in the opposite direction.
    # Assuming drag is a positive scalar that needs to be subtracted from velocity.
    if physics.get_velocity() > 0:
        velocity_after_drag = physics.get_velocity() - (physics.get_drag() * physics.get_velocity())
        # Ensure velocity doesn't flip direction due to drag alone.
        physics.set_velocity(max(0.0, velocity_after_drag))
    elif physics.get_velocity() < 0:
        velocity_after_drag = physics.get_velocity() + (physics.get_drag() * abs(physics.get_velocity()))
        # Ensure velocity doesn't flip direction due to drag alone.
        physics.set_velocity(min(0.0, velocity_after_drag))

    # Update acceleration based on force and mass.
    acceleration = physics.get_force() / physics.get_mass()

    # Update velocity with acceleration.
    physics.add_velocity(acceleration)

    displacement = physics.get_velocity() * delta_time
    transform.displace(transform.get_forward() * displacement)
    physics.set_force(0)

    return transform, physics


class PhysicsManager:
    def update(self, entity: Entity, delta_time: float):
        physics = entity.get_physics()
        transform = entity.get_transform()
        updated_transform, updated_physics = update_physics_and_transform(physics, transform, delta_time)
        entity.set_transform(updated_transform)
        entity.set_physics(updated_physics)

    def get_next_transform_and_physics(self, entity: Entity, delta_time: float) -> (Transform, Physics):
        original_physics: Physics = entity.get_physics()
        if original_physics is None:
            return entity.get_transform(), original_physics
        physics = original_physics.copy()
        original_transform = entity.get_transform()
        next_transform: Transform = original_transform.copy()
        updated_next_transform, updated_physics = update_physics_and_transform(physics, next_transform, delta_time)
        return updated_next_transform, updated_physics
