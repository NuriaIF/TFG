from __future__ import annotations

import pygame
from pygame import Surface
from pygame import Vector2

from engine.components.collider import Collider
from engine.components.physics import Physics
from engine.components.sprite import Sprite
from engine.components.transform import Transform
from engine.managers.render_manager.render_layers import RenderLayer
from engine.managers.resource_manager.sprite_loader import SpriteLoader


class EntityManager:
    def __init__(self):
        self.entities: list[int] = []

        self.transforms: list[Transform] = []
        self.physics: list[Physics] = []
        self.sprites: list[Sprite | Surface] = []
        self.colliders: list[Collider] = []

        self.batched: list[bool] = []
        self.layers: list[RenderLayer] = []

        self.next_entity_id: int = 0

    def add_entity(self, sprite_path: str, has_collider: bool = False, batched: bool = False, is_static: bool = True,
                   is_training: bool = False) -> int:
        if len(sprite_path) == 0:
            raise ValueError("Sprite path cannot be empty")

        entity_id = self.next_entity_id
        self.next_entity_id += 1

        transform = Transform()
        physics = Physics(is_static=is_static)
        sprite = SpriteLoader.load(sprite_path) if batched else Sprite(sprite_path)
        collider = Collider(sprite.get_rect(), is_active=has_collider, is_training=is_training)

        # Add components to their respective lists
        self.transforms.append(transform)
        self.physics.append(physics)
        self.sprites.append(sprite)
        self.colliders.append(collider)
        self.layers.append(RenderLayer.DEFAULT)
        self.batched.append(batched)

        # Add entity to the entity list
        self.entities.append(entity_id)

        return entity_id

    def get_transform(self, entity_id):
        return self.transforms[entity_id]

    def get_physics(self, entity_id):
        return self.physics[entity_id]

    def get_sprite(self, entity_id):
        return self.sprites[entity_id]

    def get_collider(self, entity_id):
        return self.colliders[entity_id]

    def get_layer(self, entity_id):
        return self.layers[entity_id]

    def is_batched(self, entity_id):
        return self.batched[entity_id]

    def set_layer(self, entity_id, layer: RenderLayer):
        self.layers[entity_id] = layer

    def get_sprite_rect(self, entity_id) -> pygame.Rect:
        sprite = self.get_sprite(entity_id)
        if self.batched[entity_id]:
            transform = self.get_transform(entity_id)
            return pygame.rect.Rect(transform.get_position().x, transform.get_position().y,
                                    sprite.get_width(), sprite.get_height())
        return sprite.rect

    def get_rect_with_transform(self, entity_id: int, transform: Transform) -> pygame.Rect:
        sprite = self.get_sprite(entity_id)
        if self.batched[entity_id]:
            return pygame.rect.Rect(transform.get_position().x, transform.get_position().y,
                                    sprite.get_width(), sprite.get_height())
        else:
            return pygame.rect.Rect(transform.get_position().x, transform.get_position().y,
                                    sprite.rect.width, sprite.rect.height)

    def set_transform(self, entity, updated_transform):
        self.transforms[entity] = updated_transform

    def set_physics(self, entity, updated_physics):
        self.physics[entity] = updated_physics

    def reset_entities(self):
        index = 0
        for transform in self.transforms:
            if self.layers[index] == RenderLayer.ENTITIES:
                transform.set_position(Vector2(0, 0))
            transform.set_rotation(0)
            index += 1
        for physics in self.physics:
            physics.set_velocity(0)
            physics.set_acceleration(0)
            physics.set_force(0)
