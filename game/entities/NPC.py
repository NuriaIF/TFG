from pygame import Vector2

from engine.managers.entity_manager.entity_manager import EntityManager
from engine.managers.render_manager.render_layers import RenderLayer


class NPC:
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
        entity_manager.set_layer(entity, RenderLayer.ENTITIES)
        entity_manager.get_physics(entity).set_mass(self.mass)
        entity_manager.get_physics(entity).set_drag(self.drag)
        # self.car_entity.give_collider()
        entity_manager.get_collider(entity).debug_config_show_collider()
        entity_manager.get_transform(entity).debug_config_show_transform()
        entity_manager.get_transform(entity).debug_config_show_forward()

    def set_position(self, pos: Vector2):
        self.entity_manager.get_transform(self.entity_ID).set_position(pos)
