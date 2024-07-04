from pygame import Vector2

from src.engine.managers.entity_manager.entity_manager import EntityManager
from src.engine.managers.render_manager.render_layers import RenderLayer


class NPC:
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

    def set_npc_force(self, npc_force: int):
        self.npc_force = npc_force

    def set_goal_range(self, goal_range: int):
        self.goal_range = goal_range

    def get_goal_range(self) -> int:
        return self.goal_range

    def set_road_probability(self, road_probability: float):
        self.road_probability = road_probability

    def get_road_probability(self) -> float:
        return self.road_probability

    def move_towards_goal(self):
        position = self.get_position()
        goal = self.get_goal()
        direction = goal - position
        direction.normalize_ip()
        # Make the npc look towards the goal
        self.entity_manager.get_transform(self.entity_ID).set_forward(direction)
        self.entity_manager.get_physics(self.entity_ID).add_force(self.npc_force)

    def is_on_goal(self) -> bool:
        return (self.goal - self.get_position()).magnitude() < 10

    def set_position(self, pos: Vector2):
        self.entity_manager.get_transform(self.entity_ID).set_position(pos)

    def get_position(self):
        return self.entity_manager.get_transform(self.entity_ID).get_position()

    def set_goal(self, goal: Vector2):
        self.goal = goal

    def get_goal(self):
        return self.goal
