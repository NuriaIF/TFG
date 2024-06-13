from pygame import Vector2

from engine.entities.entity import Entity
from engine.managers.input_manager.input_manager import InputManager
from engine.managers.input_manager.key import Key
from engine.managers.render_manager.render_layers import RenderLayer
from game.game_state.car_knowledge import CarKnowledge


class Car:
    """
    Car class that represents a car entity in the game.
    """
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

        self.selected_as_parent = False

        self.car_knowledge = CarKnowledge()

    def update_input(self, input_manager: InputManager) -> None:
        """
        Update the input of the car entity
        :param input_manager: input manager
        """
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

    def update(self, delta_time: float) -> None:
        """
        Update the car
        :param delta_time: time between frames
        """
        self.current_rotation_speed = self.base_rotation_speed * delta_time

    def set_position(self, pos: Vector2) -> None:
        """
        Set the position of the car
        :param pos: position to be set
        """
        self.car_entity.get_transform().set_position(pos)

    def accelerate(self) -> None:
        """
        Accelerate the car
        """
        if self.car_entity.get_physics().get_velocity() < self.accelerate_max_speed:
            self._is_accelerating = True
            self.car_entity.get_physics().set_force(self.engine_force)

    def move_forward(self) -> None:
        """
        Move the car forward
        """
        if self.car_entity.get_physics().get_velocity() < self.base_max_speed:
            self.car_entity.get_physics().set_force(self.engine_force)

    def move_backward(self) -> None:
        """
        Move the car backward
        """
        if self.car_entity.get_physics().get_velocity() > -self.base_max_speed:
            self.car_entity.get_physics().set_force(-self.engine_force)

    def rotate_right(self) -> None:
        """
        Rotate the car to the right
        """
        self.car_entity.get_transform().rotate(self.current_rotation_speed)

    def rotate_left(self) -> None:
        """
        Rotate the car to the left
        """
        self.car_entity.get_transform().rotate(-self.current_rotation_speed)

    def break_car(self) -> None:
        """
        Break the car
        """
        if self.car_entity.get_physics().get_velocity() == 0:
            return
        direction_of_velocity = self.car_entity.get_physics().get_velocity() / abs(
            self.car_entity.get_physics().get_velocity())

        self.car_entity.get_physics().set_force(self.engine_force * -direction_of_velocity)

    def is_accelerating(self) -> bool:
        """
        Check if the car is accelerating
        :return: a boolean value indicating if the car is accelerating
        """
        return self._is_accelerating

    def reset(self) -> None:
        """
        Reset the car attributes
        """
        self.car_entity.get_transform().set_position(Vector2(0, 0))
        self.car_entity.get_transform().set_rotation(0)
        self.car_entity.get_physics().set_velocity(0)
        self.car_entity.get_physics().set_acceleration(0)
        self.car_entity.get_physics().set_force(0)
        self.car_knowledge = CarKnowledge()
        self.selected_as_parent = False
