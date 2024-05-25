from pygame import Vector2

from engine.entities.entity import Entity
from engine.managers.input_manager.input_manager import InputManager
from engine.managers.input_manager.key import Key
from engine.managers.render_manager.render_layers import RenderLayer
from game.game_state.field_of_view import FOV


class Car:
    def __init__(self, entity: Entity):
        self.car_entity = entity
        self.car_entity.set_layer(RenderLayer.ENTITIES)
        self.base_max_speed = 200
        self.accelerate_max_speed = 500
        self.mass = 1000  # newtons
        self.engine_force = 10000
        self.drag = 0.005
        self.base_rotation_speed = 100
        self.current_rotation_speed = 0
        self._is_accelerating = False
        self.car_entity.get_physics().set_mass(self.mass)
        self.car_entity.get_physics().set_drag(self.drag)
        self.car_entity.give_collider()
        self.car_entity.debug_config_show_collider()
        self.car_entity.debug_config_show_transform()
        self.car_entity.debug_config_show_forward()

        self.field_of_view = FOV()
        self.last_nearest_tile = None
        self.checkpoint_number = -1
        self.current_tile_type = None
        self.distance_to_next_checkpoint = 10*16
        self.angle_to_next_checkpoint = 0
        self.selected_as_provisional_parent = False
        self.selected_as_parent = False
        self.traveled_distance = 0

    def update_input(self, input_manager: InputManager):
        self._is_accelerating = False
        if input_manager.is_key_down(Key.K_W):
            self.move_forward()
        if input_manager.is_key_down(Key.K_S):
            self.move_backward()
        if input_manager.is_key_down(Key.K_D):
            self.rotate_right()
        if input_manager.is_key_down(Key.K_A):
            self.rotate_left()

        if input_manager.is_key_down(Key.K_SHIFT):
            self.accelerate()

        # Break must be the last because it will override the other forces
        if input_manager.is_key_down(Key.K_SPACE):
            self.break_car()

    def update(self, delta_time: float):
        self.current_rotation_speed = self.base_rotation_speed * delta_time

    def set_position(self, pos: Vector2):
        self.car_entity.get_transform().set_position(pos)

    def accelerate(self):
        if self.car_entity.get_physics().get_velocity() < self.accelerate_max_speed:
            self._is_accelerating = True
            self.car_entity.get_physics().set_force(self.engine_force)

    def move_forward(self):
        if self.car_entity.get_physics().get_velocity() < self.base_max_speed:
            self.car_entity.get_physics().set_force(self.engine_force)

    def move_backward(self):
        if self.car_entity.get_physics().get_velocity() > -self.base_max_speed:
            self.car_entity.get_physics().set_force(-self.engine_force)

    def rotate_right(self):
        self.car_entity.get_transform().rotate(self.current_rotation_speed)

    def rotate_left(self):
        self.car_entity.get_transform().rotate(-self.current_rotation_speed)

    def break_car(self):
        if self.car_entity.get_physics().get_velocity() == 0:
            return
        direction_of_velocity = self.car_entity.get_physics().get_velocity() / abs(
            self.car_entity.get_physics().get_velocity())

        self.car_entity.get_physics().set_force(self.engine_force * -direction_of_velocity)

    def is_accelerating(self):
        return self._is_accelerating

    def reach_checkpoint(self, checkpoint: int):
        if checkpoint is None:
            return
        if self.checkpoint_number + 1 == checkpoint:  # or self.checkpoint_number == checkpoint - 1:
            self.checkpoint_number = checkpoint

    def set_current_tile_type(self, type_tile):
        self.current_tile_type = type_tile

    def set_distance_to_next_checkpoint(self, distance):
        self.distance_to_next_checkpoint = distance

    def set_angle_to_next_checkpoint(self, angle):
        self.angle_to_next_checkpoint = angle

    def get_traveled_distance(self):
        return self.traveled_distance

    def reset(self):
        self.car_entity.get_transform().set_position(Vector2(0, 0))
        self.car_entity.get_transform().set_rotation(0)
        self.car_entity.get_physics().set_velocity(0)
        self.car_entity.get_physics().set_acceleration(0)
        self.car_entity.get_physics().set_force(0)
        self.checkpoint_number = -1
        self.current_tile_type = None
        self.distance_to_next_checkpoint = 10*16
        self.traveled_distance = 0
