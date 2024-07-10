"""
This module contains the NPC class.
"""
from pygame import Vector2

from src.engine.managers.entity_manager.entity_manager import EntityManager
from src.engine.managers.render_manager.render_layers import RenderLayer


class NPC:
    """
    Class that represents a NPC entity in the game.
    It is a wrapper and configuration class for the NPC entity. It also handles the NPC movement.
    """
    def __init__(self, entity: int, entity_manager: EntityManager):
        self.entity_ID = entity
        self.base_max_speed = 200
        self.accelerate_max_speed = 500
        self.mass = 1000  # newtons
        self.npc_force = 400
        self.drag = 0.005
        self.base_rotation_speed = 100
        self.current_rotation_speed = 0
        self._is_accelerating = False
        self.entity_manager = entity_manager
        self.goal: Vector2 = Vector2(0, 0)
        self._is_on_goal = False
        self.goal_range = 100

        self.road_probability: float = 0.1
        entity_manager.set_layer(entity, RenderLayer.ENTITIES)
        entity_manager.get_physics(entity).set_mass(self.mass)
        entity_manager.get_physics(entity).set_drag(self.drag)
        entity_manager.get_collider(entity).debug_config_show_collider()
        entity_manager.get_transform(entity).debug_config_show_transform()
        entity_manager.get_transform(entity).debug_config_show_forward()

    def set_npc_force(self, npc_force: int) -> None:
        """
        Set the force of the NPC
        :param npc_force: force of the NPC
        :return: None
        """
        self.npc_force = npc_force

    def set_goal_range(self, goal_range: int) -> None:
        """
        Set the goal range of the NPC
        :param goal_range: goal range of the NPC
        :return: None
        """
        self.goal_range = goal_range

    def get_goal_range(self) -> int:
        """
        Get the goal range of the NPC
        :return: goal range of the NPC
        """
        return self.goal_range

    def set_road_probability(self, road_probability: float) -> None:
        """
        Set the road probability of the NPC
        :param road_probability:
        :return:
        """
        self.road_probability = road_probability

    def get_road_probability(self) -> float:
        """
        Get the road probability of the NPC
        The road probability is the probability of the NPC to set its goal to a road tile.
        :return:
        """
        return self.road_probability

    def move_towards_goal(self) -> None:
        """
        Move the NPC towards the goal
        :return: None
        """
        position = self.get_position()
        goal = self.get_goal()
        direction = goal - position
        direction.normalize_ip()
        # Make the npc look towards the goal
        self.entity_manager.get_transform(self.entity_ID).set_forward(direction)
        self.entity_manager.get_physics(self.entity_ID).add_force(self.npc_force)

    def is_on_goal(self) -> bool:
        """
        Check if the NPC is on the goal
        :return: True if the NPC is on the goal, False otherwise
        """
        return (self.goal - self.get_position()).magnitude() < 10

    def set_position(self, pos: Vector2) -> None:
        """
        Set the position of the NPC
        :param pos: position to be set
        :return: None
        """
        self.entity_manager.get_transform(self.entity_ID).set_position(pos)

    def get_position(self) -> Vector2:
        """
        Get the position of the NPC
        :return: position of the NPC
        """
        return self.entity_manager.get_transform(self.entity_ID).get_position()

    def set_goal(self, goal: Vector2) -> None:
        """
        Set the goal of the NPC
        :param goal: goal to be set
        :return: None
        """
        self.goal = goal

    def get_goal(self) -> Vector2:
        """
        Get the goal of the NPC
        :return: goal of the NPC
        """
        return self.goal
