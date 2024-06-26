import math

from pygame import Vector2

from engine.components.transform import Transform
from engine.managers.entity_manager.entity_manager import EntityManager
from game.game_state.chronometer import Chronometer
from game.game_state.field_of_view import FOV
from game.game_state.interval import Interval
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

        # intervals
        self.current_tile_interval = None
        self.tile_intervals: list[Interval] = []
        self.still_intervals: list[Interval] = []
        self.speeds_per_frame = []
        self.checkpoints_intervals = []
        self.collisions_count = 0
        self.has_collided = False

        self.counter_frames = 0
        self.accumulator_speed = 0

        self.distance_to_next_checkpoint = 0
        self.distances_to_checkpoints = []
        self.angle_to_next_checkpoint = 0

        self.last_nearest_tile = None
        self.checkpoint_number = -1
        self.checkpoint_value = -1
        self.lap_number = 0
        self.position_of_next_checkpoint = None  # used for AI inputs

        self.traveled_distance = 0  # not used

    def update(self, on_tile: MapType, next_checkpoint_position: tuple[float, float], forward: Vector2, speed: float,
               collider, car_in_tile_position: Vector2, frame_chronometer) -> None:
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
        self._update_distance_and_angle_to_next_checkpoint(next_checkpoint_position, forward, car_in_tile_position)
        self._update_tile_type(on_tile)
        self._update_collisions_count(collider)

        self._update_tile_intervals(on_tile, frame_chronometer)

    def get_field_of_view(self) -> FOV:
        """
        Get the field of view
        :return: field of view of the car
        """
        return self.field_of_view

    def get_next_checkpoint_position(self) -> tuple[float, float]:
        """
        Get the position of the next checkpoint
        :return: position of the next checkpoint
        """
        return self.position_of_next_checkpoint

    def get_angle_to_next_checkpoint(self) -> float:
        """
        Get the angle to the next checkpoint
        :return: angle to the next checkpoint
        """
        return self.angle_to_next_checkpoint

    def reach_checkpoint(self, checkpoint: int, total_checkpoints: int) -> None:
        """
        Reach the checkpoint
        :param checkpoint: number of the checkpoint
        :param total_checkpoints: total number of checkpoints
        """
        if checkpoint is None:
            return
        if self.checkpoint_number + 1 == checkpoint:  # or self.checkpoint_number == checkpoint - 1:
            self.checkpoint_number = checkpoint
            self.checkpoint_value = total_checkpoints * self.lap_number + checkpoint
        elif self.checkpoint_number == total_checkpoints - 1 and checkpoint == 0:
            self.checkpoint_number = checkpoint
            self.checkpoint_value = total_checkpoints * self.lap_number + checkpoint
            self.lap_number += 1

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
                                                      forward: Vector2, car_in_tile_position) -> None:
        """
        Update the distance and angle to the next checkpoint
        :param next_checkpoint_position: position of the next checkpoint
        :param forward: vector forward of the car
        """
        # nearest_tile = self.field_of_view.get_nearest_tile()
        # car_in_tile_position = entity_manager.get_transform(nearest_tile.entity_ID).get_position()

        self.distance_to_next_checkpoint = math.sqrt((next_checkpoint_position[0] - car_in_tile_position[0]) ** 2 +
                                                     (next_checkpoint_position[1] - car_in_tile_position[1]) ** 2)

        self.distances_to_checkpoints.append(math.sqrt((next_checkpoint_position[0] - car_in_tile_position[0]) ** 2 +
                                                       (next_checkpoint_position[1] - car_in_tile_position[1]) ** 2))
        # entity_direction = math.degrees(math.atan2(forward.y, forward.x))
        # angle_to_checkpoint = math.degrees(math.atan2(next_checkpoint_position[1] - car_in_tile_position[1],
        #                                               next_checkpoint_position[0] - car_in_tile_position[0]))
        # self.angle_to_next_checkpoint = (angle_to_checkpoint - entity_direction)
        self.angle_to_next_checkpoint = self.calculate_angle_to_checkpoint(forward, car_in_tile_position,
                                                                           next_checkpoint_position)

    def calculate_angle_to_checkpoint(self, forward, car_position, checkpoint_position):
        # Calcula el ángulo de la dirección del coche
        entity_direction = math.degrees(math.atan2(forward[1], forward[0]))

        # Calcula el ángulo hacia el checkpoint
        angle_to_checkpoint = math.degrees(math.atan2(checkpoint_position[1] - car_position[1],
                                                      checkpoint_position[0] - car_position[0]))

        # Calcula la diferencia de ángulos
        angle_difference = angle_to_checkpoint - entity_direction

        # Normaliza el ángulo a estar en el rango -180 a 180 grados
        while angle_difference > 180:
            angle_difference -= 360
        while angle_difference < -180:
            angle_difference += 360

        return angle_difference

    def _update_tile_type(self, on_tile) -> None:
        """
        Update the nearest tile
        :param on_tile: type of the tile the car is on
        """
        if on_tile == MapType.SIDEWALK:
            self.has_collided = True
        if self.last_nearest_tile != on_tile:
            self.last_nearest_tile = on_tile

    def _update_collisions_count(self, collider) -> None:
        """
        Update the collisions count
        """
        if collider.is_colliding():
            self.has_collided = True
            self.collisions_count += 1

    def _update_still_chronometer(self, speed) -> None:
        """
        Update the still chronometer (time the car is still)
        :param speed: speed of the car
        """
        if speed < 0.1:
            self.chronometer_still.start()
        else:
            self.chronometer_still.stop()

    def _update_tile_intervals(self, on_tile: MapType, frame_chronometer: Chronometer) -> None:
        if self.current_tile_interval == on_tile:
            return

        if len(self.tile_intervals) > 0:
            self.tile_intervals[-1].close(frame_chronometer.get_elapsed_time())
        self.tile_intervals.append(Interval(frame_chronometer.get_elapsed_time(), on_tile))
        self.current_tile_interval = on_tile
