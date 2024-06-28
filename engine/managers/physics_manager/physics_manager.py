from engine.components.physics import Physics
from engine.components.transform import Transform
from engine.managers.entity_manager.entity_manager import EntityManager


class PhysicsManager:
    def update(self, entity: int, physics: Physics, transform: Transform, entity_manager: EntityManager,
               delta_time: float):
        if physics.is_static():
            return
        updated_transform, updated_physics = self._update_physics_and_transform(physics, transform, delta_time)
        entity_manager.set_transform(entity, updated_transform)
        entity_manager.set_physics(entity, updated_physics)

    def _update_physics_and_transform(self, physics: Physics, transform: Transform, delta_time: float) \
            -> (Transform, Physics):
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
        velocity_after_drag = physics.get_vector_velocity() - (physics.get_drag() * physics.get_vector_velocity())
        physics.set_vector_velocity(velocity_after_drag)

        # Update acceleration based on force and mass.
        acceleration = physics.get_force() / physics.get_mass()

        # Update velocity with acceleration.
        physics.add_velocity(acceleration)

        displacement = physics.get_velocity() * delta_time
        transform.displace(transform.get_forward() * displacement)
        transform.displace(physics.get_vector_velocity() * delta_time)
        physics.set_force(0)

        return transform, physics
