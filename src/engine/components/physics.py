"""
This module contains the Physics class
"""
from pygame import Vector2


class Physics:
    """
    The class physics represents the physical attributes of an object related to its movement like mass or velocity.
    It has the following attributes:

    - mass: the mass represents the amount of matter in the object, and the more mass, the more force is needed to move
      it. It is a scalar value greater than 0.


    - force: The force represents the push force an object is receiving toward it's forward direction. It is a scalar
      value that can be positive or negative. If negative, it represents a backward force, if positive, a forward force.

    - acceleration: the acceleration represents the amount of velocity an object is gaining in a fixed amount of time.
      This is calculated from the force and the mass of the object.
      It is a scalar value that can be positive or negative.

    - velocity: the velocity represents the amount of distance the object covers in a fixed amount of time.
      It is a scalar value that can be positive or negative.

    - drag: the drag represents the amount of drag (resistance) the object has while moving. This is a scalar value that
      multiplies the velocity and decreases it every frame.

    - vector_velocity: the velocity of the object in a 2D space. This is a vector that represents the velocity in the x
      and y-axis, and therefore allows the objects to have non-forward movement.

    - is_static: a boolean value that represents if the object is static or not. If it is static, it will not move in
      any way.
    """
    def __init__(self, is_static):
        self.mass: float = 1
        self.velocity: float = 0
        self.acceleration: float = 0
        self.force: float = 0
        self.drag: float = 0.1
        self._is_static: bool = is_static
        self._vector_velocity: Vector2 = Vector2(0, 0)

    def add_acceleration(self, acceleration: float) -> None:
        """
        Add acceleration to the current forward acceleration
        :param acceleration: a scalar value to add to the current acceleration
        :return: None
        """
        self.acceleration += acceleration

    def add_velocity(self, velocity: float) -> None:
        """
        Add velocity to the current forward velocity
        :param velocity: a scalar value to add to the current velocity
        :return: None
        """
        self.velocity += velocity

    def decrease_velocity(self, velocity: float) -> None:
        """
        Decrease velocity to the current forward velocity
        :param velocity: a scalar value to decrease to the current velocity
        :return: None
        """
        self.velocity -= velocity

    def add_force(self, force: float) -> None:
        """
        Add force to the current forward force
        :param force: a scalar value to add to the current force
        :return: None
        """
        self.force += force

    def get_drag(self) -> float:
        """
        Get the drag of the physics.
        :return:
        """
        return self.drag

    def set_drag(self, drag: float) -> None:
        """
        Set the drag of the physics.
        :param drag: the drag value to set between 0 and 1
        :return:
        """
        self.drag = drag

    def get_mass(self) -> float:
        """
        Get the mass of the physics object
        :return: the mass of the object (value greater than 0)
        """
        return self.mass

    def get_velocity(self) -> float:
        """
        Get the velocity of the physics object
        :return:
        """
        return self.velocity

    def get_force(self) -> float:
        """
        Get the force of the physics object
        :return:
        """
        return self.force

    def get_acceleration(self) -> float:
        """
        Get the acceleration of the physics object
        :return: The acceleration of the object
        """
        return self.acceleration

    def set_mass(self, mass: float) -> None:
        """
        Set the mass of the physics object
        :param mass: the mass of the object (value greater than 0)
        :return: none
        """
        if mass < 0:
            raise ValueError("Mass cannot be negative")
        self.mass = mass

    def set_vector_velocity(self, vector_velocity: Vector2) -> None:
        """
        Set the velocity of the physics object in a 2D space
        :param vector_velocity: the velocity of the object in a 2D space (x, y)
        :return: none
        """
        self._vector_velocity = vector_velocity

    def get_vector_velocity(self) -> Vector2:
        """
        Get the velocity of the physics object in a 2D space
        :return: the velocity of the object in a 2D space (x, y)
        """
        return self._vector_velocity

    def set_velocity(self, velocity: float) -> None:
        """
        Set the forward velocity of the physics object
        :param velocity: the velocity of the object
        :return: none
        """
        self.velocity = velocity

    def set_acceleration(self, acceleration: float) -> None:
        """
        Set the acceleration of the physics object
        :param acceleration: the acceleration of the object
        :return: none
        """
        self.acceleration = acceleration

    def set_force(self, force_vector: float) -> None:
        """
        Set the force of the physics object
        :param force_vector: the force of the object
        :return: none
        """
        self.force = force_vector

    def is_static(self) -> bool:
        """
        Check if the object is static, if it is, it will not move
        :return: True if the object is static, False otherwise
        """
        return self._is_static

    def set_static(self, is_static: bool) -> None:
        """
        Set the object to be static or not
        If it is static, it will not move
        :param is_static: True if the object is static, False otherwise
        :return: none
        """
        self._is_static = is_static

    def copy(self) -> 'Physics':
        """
        Copy the physics object
        :return: a copy of the physics object
        """
        physics = Physics(self.is_static())
        physics.mass = self.mass
        physics.velocity = self.velocity
        physics.acceleration = self.acceleration
        physics.force = self.force
        physics.drag = self.drag
        return physics

    def reset(self) -> None:
        """
        Totally reset the physics object
        :return: none
        """
        self.velocity = 0
        self._vector_velocity = Vector2(0, 0)
        self.acceleration = 0
        self.force = 0
