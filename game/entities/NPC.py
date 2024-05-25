from pygame import Vector2

from engine.entities.entity import Entity
from engine.managers.render_manager.render_layers import RenderLayer


class NPC:
    def __init__(self, entity: Entity):
        self.NPC_entity = entity
        self.NPC_entity.set_layer(RenderLayer.ENTITIES)
        self.base_max_speed = 200
        self.accelerate_max_speed = 500
        self.mass = 1000  # newtons
        self.engine_force = 10000
        self.drag = 0.005
        self.base_rotation_speed = 100
        self.current_rotation_speed = 0
        self._is_accelerating = False
        self.NPC_entity.get_physics().set_mass(self.mass)
        self.NPC_entity.get_physics().set_drag(self.drag)
        self.NPC_entity.give_collider()
        self.NPC_entity.debug_config_show_collider()
        self.NPC_entity.debug_config_show_transform()
        self.NPC_entity.debug_config_show_forward()

    def set_position(self, pos: Vector2):
        self.NPC_entity.get_transform().set_position(pos)
