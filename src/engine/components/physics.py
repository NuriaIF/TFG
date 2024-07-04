from pygame import Vector2


class Physics:
    def __init__(self, is_static):
        self.mass: float = 1
        self.velocity: float = 0
        self.acceleration: float = 0
        self.force: float = 0
        self.drag: float = 0.1
        self._is_static: bool = is_static
        self._vector_velocity: Vector2 = Vector2(0, 0)

    def add_acceleration(self, acceleration: float) -> None:
        self.acceleration += acceleration

    def add_velocity(self, velocity: float) -> None:
        self.velocity += velocity

    def decrease_velocity(self, velocity: float) -> None:
        self.velocity -= velocity

    def add_force(self, force: float) -> None:
        self.force += force

    def get_drag(self) -> float:
        return self.drag

    def set_drag(self, drag: float) -> None:
        self.drag = drag

    def get_mass(self) -> float:
        return self.mass

    def get_velocity(self) -> float:
        return self.velocity

    def get_force(self) -> float:
        return self.force

    def get_acceleration(self) -> float:
        return self.acceleration

    def set_mass(self, mass: float) -> None:
        if mass < 0:
            raise ValueError("Mass cannot be negative")
        self.mass = mass

    def set_vector_velocity(self, vector_velocity: Vector2) -> None:
        self._vector_velocity = vector_velocity

    def get_vector_velocity(self) -> Vector2:
        return self._vector_velocity

    def set_velocity(self, velocity: float) -> None:
        self.velocity = velocity

    def set_acceleration(self, acceleration: float) -> None:
        self.acceleration = acceleration

    def set_force(self, force_vector: float) -> None:
        self.force = force_vector

    def is_static(self) -> bool:
        return self._is_static

    def set_static(self, is_static: bool) -> None:
        self._is_static = is_static

    def copy(self) -> 'Physics':
        physics = Physics(self.is_static())
        physics.mass = self.mass
        physics.velocity = self.velocity
        physics.acceleration = self.acceleration
        physics.force = self.force
        physics.drag = self.drag
        return physics

    def reset(self) -> None:
        self.velocity = 0
        self._vector_velocity = Vector2(0, 0)
        self.acceleration = 0
        self.force = 0
