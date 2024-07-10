"""
This transform component is responsible for storing the position, rotation, and scale of an entity.
"""
import copy
import math

from pygame import Vector2


class Transform:
    """
    The Transform component is responsible for storing the position, rotation, and scale of an entity.
    It also has methods to obtain the forward vector of the entity and to manipulate the position, rotation, and scale.
    """
    def __init__(self):
        self._position = Vector2(0, 0)
        self._rotation = 0
        self._scale = Vector2(1, 1)
        self._transform_debug_show: bool = False
        self._forward_debug_show: bool = False

    def __eq__(self, other: 'Transform') -> bool:
        """
        Check if two transforms are equal.
        :param other: The other transform to compare to
        :return: True if the transforms are equal, False otherwise
        """
        if self is other:
            return True
        return self._position == other._position and self._rotation == other._rotation and self._scale == other._scale

    def __deepcopy__(self, memodict=None) -> 'Transform':
        """
        Deepcopy the transform
        :param memodict: The memo dictionary
        :return: A deepcopy of the transform
        """
        if memodict is None:
            memodict = {}
        cls = self.__class__
        result = cls.__new__(cls)
        memodict[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memodict))  # Use deepcopy for attributes
        return result

    def displace(self, displacement: Vector2) -> None:
        """
        Displace the entity by a given displacement vector.
        :param displacement: The displacement vector
        :return: None
        """
        # if not isinstance(displacement, Vector2):
        #     raise ValueError("Displacement must be a Vector2")
        self._position += displacement

    def get_position(self) -> Vector2:
        """
        Get the position of the entity.
        :return: The position of the entity
        """
        return self._position

    def set_position_x(self, x: float) -> None:
        """
        Set the x position of the entity.
        :param x: The x position
        :return: None
        """
        # if not isinstance(x, (int, float)):
        #     raise ValueError("X must be a number")
        self._position[0] = x

    def set_position_y(self, y: float) -> None:
        """
        Set the y position of the entity.
        :param y: The y position
        :return: None
        """
        # if not isinstance(y, (int, float)):
        #     raise ValueError("Y must be a number")
        self._position[1] = y

    def set_position(self, position: Vector2) -> None:
        """
        Set the position of the entity with a given position vector.
        :param position: The position vector
        :return: None
        """
        # if not isinstance(position, Vector2):
        #     raise ValueError("Position must be a Vector2")
        self._position = position

    def get_rotation(self) -> float:
        """
        Get the rotation of the entity.
        :return: The rotation of the entity
        """
        return self._rotation

    def set_rotation(self, rotation: float) -> None:
        """
        Set the rotation of the entity.
        :param rotation: The rotation of the entity
        :return: None
        """
        # if not isinstance(rotation, (int, float)):
        #     raise ValueError("Rotation must be a number")
        self._rotation = rotation

    def get_scale(self) -> Vector2:
        """
        Get the scale of the entity.
        :return: The scale of the entity
        """
        return self._scale

    def set_scale(self, scale: Vector2) -> None:
        """
        Set the scale of the entity with a given scale vector.
        :param scale: The scale vector
        :return: None
        """
        # if not isinstance(scale, Vector2):
        #     raise ValueError("Scale must be a Vector2")

        if scale.x < 0:
            scale.x = max(0.0, scale.x)
        if scale.y < 0:
            scale.y = max(0.0, scale.y)
        self._scale = scale

    def rotate(self, angle: float) -> None:
        """
        Rotate the entity by a given angle.
        If the angle is positive, the entity rotates counter-clockwise.
        If the angle is negative, the entity rotates clockwise.
        If the angle is greater than 360 or less than -360, the angle is wrapped around.
        :param angle:
        :return:
        """
        self._rotation += angle
        self._rotation %= 360

    def get_forward(self) -> Vector2:
        """
        Get the forward vector of the entity.
        It is calculated using the rotation of the entity.
        :return: The forward vector of the entity
        """
        # Convert rotation to radians because math trig functions expect radians
        radians = math.radians(self._rotation)

        forward_x = math.sin(-radians)
        forward_y = math.cos(radians)  # Add pi to rotate 180 degrees, forward starts looking up

        return -Vector2(forward_x, forward_y).normalize()

    def set_forward(self, forward: Vector2) -> None:
        """
        Set the forward vector of the entity.
        It will change the rotation of the entity to make the forward vector the new forward vector.
        :param forward:
        :return:
        """
        self._rotation = math.degrees(math.atan2(forward.y, forward.x)) + 90

    def shows_debug_transform(self) -> bool:
        """
        Returns whether the transform should be shown in debug mode.
        :return: True if the transform should be shown, False otherwise
        """
        return self._transform_debug_show

    def shows_debug_forward(self) -> bool:
        """
        Returns whether the forward vector should be shown in debug mode.
        :return:
        """
        return self._forward_debug_show

    def copy(self) -> 'Transform':
        """
        Create a copy of the transform.
        :return:
        """
        new_transform = Transform()
        new_transform._position = self._position.copy()
        new_transform._scale = self._scale.copy()
        return new_transform

    def debug_config_show_transform(self) -> None:
        """
        Sets the transform to be shown in debug mode.
        :return: None
        """
        self._transform_debug_show = True

    def debug_config_show_forward(self) -> None:
        """
        Sets the forward vector to be shown in debug mode.
        :return: None
        """
        self._forward_debug_show = True

    def debug_config_hide_transform(self) -> None:
        """
        Hides the transform in debug mode.
        :return: None
        """
        self._transform_debug_show = False

    def debug_config_hide_forward(self) -> None:
        """
        Hides the forward vector in debug mode.
        :return: None
        """
        self._forward_debug_show = False

    def reset(self):
        """
        Totally resets the transform.
        Sets position to (0, 0), rotation to 0, scale to (1, 1), and hides the transform and forward vector in
        debug mode.
        :return:
        """
        self._position = Vector2(0, 0)
        self._rotation = 0
        self._scale = Vector2(1, 1)
        self._transform_debug_show = False
        self._forward_debug_show = False
