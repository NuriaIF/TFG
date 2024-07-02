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

        self.sprite_rects: list[pygame.Rect] = []
        self.next_frame_sprite_rects: list[pygame.Rect] = []

        self.batched: list[bool] = []
        self.layers: list[RenderLayer] = []

        self.next_entity_id: int = 0

    def create_entity(self, sprite_path: str, has_collider: bool = False, batched: bool = False, is_static: bool = True) -> int:
        if len(sprite_path) == 0:
            raise ValueError("Sprite path cannot be empty")

        entity_id = self.next_entity_id
        self.next_entity_id += 1

        transform = Transform()
        physics = Physics(is_static=is_static)
        sprite = SpriteLoader.load(sprite_path) if batched else Sprite(sprite_path)
        collider = Collider(sprite.get_rect(), is_active=has_collider)

        # Add components to their respective lists
        self.transforms.append(transform)
        self.physics.append(physics)
        self.sprites.append(sprite)
        self.colliders.append(collider)
        self.layers.append(RenderLayer.DEFAULT)
        self.batched.append(batched)
        if batched:
            self.sprite_rects.append(pygame.rect.Rect(transform.get_position().x, transform.get_position().y,
                                                      sprite.get_width(), sprite.get_height()))
            self.next_frame_sprite_rects.append(pygame.rect.Rect(transform.get_position().x, transform.get_position().y,
                                                                 sprite.get_width(), sprite.get_height()))
        else:
            self.sprite_rects.append(sprite.rect)
            self.next_frame_sprite_rects.append(sprite.rect)

        # Add entity to the entity list
        self.entities.append(entity_id)

        return entity_id

    def get_transform(self, entity_id) -> Transform:
        return self.transforms[entity_id]

    def get_physics(self, entity_id) -> Physics:
        return self.physics[entity_id]

    def get_sprite(self, entity_id) -> Sprite | Surface:
        return self.sprites[entity_id]

    def get_collider(self, entity_id) -> Collider:
        return self.colliders[entity_id]

    def get_layer(self, entity_id) -> RenderLayer:
        return self.layers[entity_id]

    def is_batched(self, entity_id) -> bool:
        return self.batched[entity_id]

    def set_layer(self, entity_id, layer: RenderLayer) -> None:
        self.layers[entity_id] = layer

    def get_sprite_rect(self, entity_id) -> pygame.Rect:
        if self.batched[entity_id]:
            position = self.get_transform(entity_id).get_position()
            rect = self.sprite_rects[entity_id]
            rect.x = position.x
            rect.y = position.y
            return rect

        sprite = self.get_sprite(entity_id)
        return sprite.rect

    def get_next_frame_sprite_rect(self, entity_id) -> pygame.Rect:
        return self.next_frame_sprite_rects[entity_id]

    def get_rect_with_transform(self, entity_id: int, transform: Transform) -> pygame.Rect:
        position = transform.get_position()
        rect = self.get_next_frame_sprite_rect(entity_id)
        rect.x = position.x
        rect.y = position.y

        return rect

    def set_transform(self, entity, updated_transform):
        self.transforms[entity] = updated_transform

    def set_physics(self, entity, updated_physics):
        self.physics[entity] = updated_physics

    def reset_entity(self, entity_id):
        self.get_transform(entity_id).reset()
        self.get_physics(entity_id).reset()
        self.get_collider(entity_id).reset()

    def clear(self):
        self.entities.clear()
        self.transforms.clear()
        self.physics.clear()
        self.sprites.clear()
        self.colliders.clear()
        self.sprite_rects.clear()
        self.next_frame_sprite_rects.clear()
        self.batched.clear()
        self.layers.clear()
        self.next_entity_id = 0

