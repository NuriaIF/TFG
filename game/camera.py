from pygame import Vector2

from engine.entities.entity import Entity


class Camera:
    def __init__(self, window_size: Vector2):
        self._delta_time: float = 0
        self._window_size: Vector2 = window_size

        self._position: Vector2 = Vector2(self._window_size / 2)
        self._previous_position: Vector2 = self._position
        self._displacement: Vector2 = Vector2(0, 0)
        self._moving: bool = False

    def get_displacement(self) -> Vector2:
        return self._displacement

    def set_position(self, position: Vector2) -> None:
        self._previous_position = self._position
        self._position = position

    def reset_position(self):
        self._delta_time: float = 0

        self._position: Vector2 = Vector2(self._window_size / 2)
        self._previous_position: Vector2 = self._position
        self._displacement: Vector2 = Vector2(0, 0)
        self._moving: bool = False

    def update(self, delta_time: float, entities: list[Entity]) -> None:
        self._delta_time = delta_time

        # Calculate displacement based on the change in position
        self._displacement = self._previous_position - self._position
        if self._displacement.length() > 0.01:  # Check if there's any displacement

            for entity in entities:
                # Displace all entities, with negative value, because when the camera moves to the right, the entities
                # should move to the left, and vice versa, and same with up and down
                entity.get_transform().displace(-self._displacement)

            self._previous_position = self._position

    def move(self, displacement: Vector2) -> None:
        self.set_position(self._position + displacement * self._delta_time)

    def get_position(self) -> Vector2:
        return self._position
