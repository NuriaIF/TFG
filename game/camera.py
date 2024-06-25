from pygame import Vector2

from engine.components.transform import Transform


class Camera:
    def __init__(self, window_size: Vector2):
        self._delta_time: float = 0
        self._window_size: Vector2 = window_size

        self._position: Vector2 = Vector2(0,0)
        self._previous_position: Vector2 = self._position
        self._displacement: Vector2 = Vector2(0, 0)
        self._moving: bool = False

    def set_position(self, position: Vector2) -> None:
        self._previous_position = self._position
        self._position = position

    def reset_position(self):
        self._delta_time: float = 0

        self._position: Vector2 = Vector2(self._window_size / 2)
        self._previous_position: Vector2 = self._position
        self._displacement: Vector2 = Vector2(0, 0)
        self._moving: bool = False

    def update(self, delta_time: float) -> None:
        self._delta_time = delta_time

        # Calculate displacement based on the change in position
        self._displacement = self._previous_position - self._position
        if self._displacement.length() > 0.01:  # Check if there's any displacement
            self._previous_position = self._position

    def move(self, displacement: Vector2) -> None:
        self.set_position(self._position + displacement * self._delta_time)

    def get_position(self) -> Vector2:
        return self._position
