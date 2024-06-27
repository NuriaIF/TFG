import copy
import math

from pygame import Vector2


class Transform:
    def __init__(self):
        self._position = Vector2(0, 0)
        self._rotation = 0
        self._scale = Vector2(1, 1)
        self._transform_debug_show: bool = False
        self._forward_debug_show: bool = False

    def __eq__(self, other: 'Transform') -> bool:
        if self is other:
            return True
        return self._position == other._position and self._rotation == other._rotation and self._scale == other._scale

    def __deepcopy__(self, memodict={}):
        cls = self.__class__
        result = cls.__new__(cls)
        memodict[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memodict))  # Use deepcopy for attributes
        return result

    def displace(self, displacement: Vector2) -> None:
        # if not isinstance(displacement, Vector2):
        #     raise ValueError("Displacement must be a Vector2")
        self._position += displacement

    def get_position(self) -> Vector2:
        return self._position

    def set_position_x(self, x: float) -> None:
        # if not isinstance(x, (int, float)):
        #     raise ValueError("X must be a number")
        self._position[0] = x

    def set_position_y(self, y: float) -> None:
        # if not isinstance(y, (int, float)):
        #     raise ValueError("Y must be a number")
        self._position[1] = y

    def set_position(self, position: Vector2) -> None:
        # if not isinstance(position, Vector2):
        #     raise ValueError("Position must be a Vector2")
        self._position = position

    def get_rotation(self) -> float:
        return self._rotation

    def set_rotation(self, rotation: float) -> None:
        # if not isinstance(rotation, (int, float)):
        #     raise ValueError("Rotation must be a number")
        self._rotation = rotation

    def get_scale(self) -> Vector2:
        return self._scale

    def set_scale(self, scale: Vector2) -> None:
        # if not isinstance(scale, Vector2):
        #     raise ValueError("Scale must be a Vector2")

        if scale.x < 0:
            scale.x = max(0.0, scale.x)
        if scale.y < 0:
            scale.y = max(0.0, scale.y)
        self._scale = scale

    def rotate(self, angle: float) -> None:
        self._rotation += angle
        self._rotation %= 360

    def get_forward(self) -> Vector2:
        # Convert rotation to radians because math trig functions expect radians
        radians = math.radians(self._rotation)

        forward_x = math.sin(radians)
        forward_y = math.cos(radians + math.pi)  # Add pi to rotate 180 degrees, forward starts looking up

        return Vector2(forward_x, forward_y).normalize()

    def set_forward(self, forward: Vector2) -> None:
        self._rotation = math.degrees(math.atan2(forward.y, forward.x)) + 90

    def shows_debug_transform(self) -> bool:
        return self._transform_debug_show

    def shows_debug_forward(self) -> bool:
        return self._forward_debug_show

    # def copy(self) -> 'Transform':
    #     return copy.deepcopy(self)
    # 
    def copy(self) -> 'Transform':
        new_transform = Transform()
        new_transform._position = self._position.copy()
        new_transform._rotation = self._rotation
        new_transform._scale = self._scale.copy()
        return new_transform

    def debug_config_show_transform(self) -> None:
        self._transform_debug_show = True

    def debug_config_show_forward(self) -> None:
        self._forward_debug_show = True

    def debug_config_hide_transform(self) -> None:
        self._transform_debug_show = False

    def debug_config_hide_forward(self) -> None:
        self._forward_debug_show = False

    def reset(self):
        self._position = Vector2(0, 0)
        self._rotation = 0
        self._scale = Vector2(1, 1)
        self._transform_debug_show = False
        self._forward_debug_show = False
