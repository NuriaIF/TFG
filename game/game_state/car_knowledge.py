import math

from pygame import Vector2

from engine.components.transform import Transform
from engine.managers.entity_manager.entity_manager import EntityManager
from game.game_state.chronometer import Chronometer
from game.game_state.field_of_view import FOV
from game.map.map_types import MapType


class CarKnowledge():
    """
    Class that represents the car knowledge in the game.
    """
    def __init__(self) -> None:
        self.field_of_view = FOV()

        self.chronometer_track = Chronometer()
        self.chronometer_sidewalk = Chronometer()
        self.chronometer_grass = Chronometer()
        self.chronometer_still = Chronometer()

        self.counter_frames = 0
        self.accumulator_speed = 0

        self.distance_to_next_checkpoint = 0
        self.angle_to_next_checkpoint = 0

        self.last_nearest_tile = None
        self.checkpoint_number = -1
        self.position_of_next_checkpoint = None  # used for AI inputs

        self.traveled_distance = 0  # not used

        self.angle_difference = 0

    def update(self, on_tile: MapType, next_checkpoint_position: tuple[float, float], forward: Vector2, speed: float,
               entity_manager: EntityManager, transform: Transform) -> None:
        """
        Update the car knowledge
        :param on_tile: type of the tile the car is on
        :param next_checkpoint_position: position of the next checkpoint
        :param forward: vector forward of the car
        :param speed: speed of the car
        :param entity_manager: entity manager of the game
        """
        self.position_of_next_checkpoint = next_checkpoint_position
        self.counter_frames += 1
        self._update_tile_chronometers(on_tile)
        self._update_still_chronometer(speed)
        self._update_speed_accumulator(speed)
        self._update_distance_and_angle_to_next_checkpoint(next_checkpoint_position, forward, entity_manager)
        self._update_tile_type(on_tile)
        self._calculate_angle_difference(transform)

    def get_field_of_view(self) -> FOV:
        """
        Get the field of view
        :return: field of view of the car
        """
        return self.field_of_view

    def get_next_checkpoint_position(self) -> tuple[float, float]:
        """
        Get the next checkpoint position
        :return: position of the next checkpoint
        """
        return self.position_of_next_checkpoint

    def reach_checkpoint(self, checkpoint: int) -> None:
        """
        Reach the checkpoint
        :param checkpoint: number of the checkpoint
        """
        if checkpoint is None:
            return
        if self.checkpoint_number + 1 == checkpoint:  # or self.checkpoint_number == checkpoint - 1:
            self.checkpoint_number = checkpoint

    def _update_tile_chronometers(self, on_tile: MapType) -> None:
        """
        Update the chronometers of the tiles the car is on
        :param on_tile: type of the tile the car is on
        """
        if on_tile == MapType.TRACK:
            self.chronometer_track.start()
            self.chronometer_sidewalk.stop()
            self.chronometer_grass.stop()
        elif on_tile == MapType.SIDEWALK:
            self.chronometer_sidewalk.start()
            self.chronometer_track.stop()
            self.chronometer_grass.stop()
        elif on_tile == MapType.GRASS:
            self.chronometer_grass.start()
            self.chronometer_sidewalk.stop()
            self.chronometer_track.stop()

    def _update_speed_accumulator(self, speed: float) -> None:
        """
        Update the speed accumulator
        :param speed: speed of the car
        """
        self.accumulator_speed += speed

    def _update_distance_and_angle_to_next_checkpoint(self, next_checkpoint_position: tuple[float, float],
                                                      forward: Vector2, entity_manager: EntityManager) -> None:
        """
        Update the distance and angle to the next checkpoint
        :param next_checkpoint_position: position of the next checkpoint
        :param forward: vector forward of the car
        """
        nearest_tile = self.field_of_view.get_nearest_tile()
        car_in_tile_position = entity_manager.get_transform(nearest_tile.entity_ID).get_position()

        self.distance_to_next_checkpoint = math.sqrt((next_checkpoint_position[0] - car_in_tile_position[0]) ** 2 +
                                                     (next_checkpoint_position[1] - car_in_tile_position[1]) ** 2)

        entity_direction = math.degrees(math.atan2(forward.y, forward.x))
        angle_to_checkpoint = math.degrees(math.atan2(next_checkpoint_position[1] - car_in_tile_position[1],
                                                      next_checkpoint_position[0] - car_in_tile_position[0]))
        self.angle_to_next_checkpoint = abs(angle_to_checkpoint - entity_direction)

    def _update_tile_type(self, on_tile) -> None:
        """
        Update the nearest tile
        :param on_tile: type of the tile the car is on
        """
        if self.last_nearest_tile != on_tile:
            self.last_nearest_tile = on_tile

    def _update_still_chronometer(self, speed) -> None:
        """
        Update the still chronometer (time the car is still)
        :param speed: speed of the car
        """
        if speed < 0.1:
            self.chronometer_still.start()
        else:
            self.chronometer_still.stop()

    def _calculate_angle_difference(self, transform: Transform) -> None:
        forward = transform.get_forward()
        entity_direction = math.degrees(math.atan2(forward.y, forward.x))

        angle_to_checkpoint = self.angle_to_next_checkpoint
        angle_difference = abs(angle_to_checkpoint - entity_direction)

        self.angle_difference = angle_difference
