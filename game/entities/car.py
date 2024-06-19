from pygame import Vector2

from engine.managers.entity_manager.entity_manager import EntityManager
from engine.managers.input_manager.input_manager import InputManager
from engine.managers.input_manager.key import Key
from engine.managers.render_manager.render_layers import RenderLayer
from game.game_state.car_knowledge import CarKnowledge


class Car:
    """
    Car class that represents a car entity in the game.
    """
    def __init__(self, entity: int, entity_manager: EntityManager):
        self.entity_ID = entity
        self.base_max_speed = 200
        self.accelerate_max_speed = 500
        self.mass = 1000  # newtons
        self.engine_force = 10000
        self.drag = 0.005
        self.base_rotation_speed = 100
        self.current_rotation_speed = 0
        self._is_accelerating = False
        self.entity_manager = entity_manager
        self.entity_manager.set_layer(entity, RenderLayer.ENTITIES)
        self.entity_manager.get_physics(entity).set_mass(self.mass)
        self.entity_manager.get_physics(entity).set_drag(self.drag)
        # self.car_entity.give_collider()
        self.entity_manager.get_collider(entity).debug_config_show_collider()
        self.entity_manager.get_transform(entity).debug_config_show_transform()
        self.entity_manager.get_transform(entity).debug_config_show_forward()

        self.selected_as_parent = False

        self.car_knowledge = CarKnowledge()
        self.fitness_score = 0

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
        self.entity_manager.get_transform(self.entity_ID).set_position(pos)

    def accelerate(self) -> None:
        """
        Accelerate the car
        """
        if self.entity_manager.get_physics(self.entity_ID).get_velocity() < self.accelerate_max_speed:
            self._is_accelerating = True
            self.entity_manager.get_physics(self.entity_ID).set_force(self.engine_force)

    def move_forward(self) -> None:
        """
        Move the car forward
        """
        if self.entity_manager.get_physics(self.entity_ID).get_velocity() < self.base_max_speed:
            self.entity_manager.get_physics(self.entity_ID).set_force(self.engine_force)

    def move_backward(self) -> None:
        """
        Move the car backward
        """
        if self.entity_manager.get_physics(self.entity_ID).get_velocity() > -self.base_max_speed:
            self.entity_manager.get_physics(self.entity_ID).set_force(-self.engine_force)

    def rotate_right(self) -> None:
        """
        Rotate the car to the right
        """
        self.entity_manager.get_transform(self.entity_ID).rotate(self.current_rotation_speed)

    def rotate_left(self) -> None:
        """
        Rotate the car to the left
        """
        self.entity_manager.get_transform(self.entity_ID).rotate(-self.current_rotation_speed)

    def break_car(self) -> None:
        """
        Break the car
        """
        if self.entity_manager.get_physics(self.entity_ID).get_velocity() == 0:
            return
        direction_of_velocity = self.entity_manager.get_physics(self.entity_ID).get_velocity() / abs(
            self.entity_manager.get_physics(self.entity_ID).get_velocity())

        self.entity_manager.get_physics(self.entity_ID).set_force(self.engine_force * -direction_of_velocity)

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
        self.car_knowledge = CarKnowledge()
        self.selected_as_parent = False

    def set_fitness(self, fitness_score):
        """
        Set the fitness score of the car
        :param fitness_score: fitness score to be set
        """
        self.fitness_score = fitness_score
