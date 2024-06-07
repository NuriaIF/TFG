from __future__ import annotations

import pygame
from pygame import Surface

from engine.components.collider import Collider
from engine.components.physics import Physics
from engine.components.sprite import Sprite
from engine.components.transform import Transform
from engine.managers.render_manager.render_layers import RenderLayer
from engine.managers.resource_manager.sprite_loader import SpriteLoader


class Entity:
    def __init__(self, sprite_path: str, use_engine_physics: bool = True, has_collider: bool = False,
                 batched: bool = False, is_static: bool = True, is_training: bool = False):
        if len(sprite_path) == 0:
            raise ValueError("Sprite path cannot be empty")
        self._transform: Transform = Transform()

        self._physics: Physics | None = Physics() if use_engine_physics and not is_static else None

        self._transform_debug_show: bool = False
        self._collider_debug_show: bool = False
        self._forward_debug_show: bool = False

        self._has_collider: bool = has_collider
        self._is_static: bool = is_static

        self._is_batched: bool = batched
        self._sprite: Surface | Sprite = SpriteLoader.load(sprite_path) if batched else Sprite(sprite_path)
        self._collider: Collider | None = Collider(self.get_sprite_rect(), is_training) if has_collider else None

        # If the entity is batched contains just a surface, otherwise it contains a sprite
        self._is_already_batched: bool = False

        self.fitness = None

    def is_static(self) -> bool:
        return self._is_static

    def give_collider(self) -> None:
        if not self._has_collider:
            self._has_collider = True
            self._collider: Collider | None = Collider(self.get_sprite_rect())

    def get_sprite_rect(self) -> pygame.Rect:
        if self.is_batched():
            return pygame.rect.Rect(self._transform.get_position().x, self._transform.get_position().y,
                                    self._sprite.get_width(), self._sprite.get_height())
        return self._sprite.rect

    def get_rect_with_transform(self, transform: Transform) -> pygame.Rect:
        if self.is_batched():
            return pygame.rect.Rect(transform.get_position().x, transform.get_position().y,
                                    self._sprite.get_width(), self._sprite.get_height())
        else:
            return pygame.rect.Rect(transform.get_position().x, transform.get_position().y,
                                    self._sprite.rect.width, self._sprite.rect.height)

    def set_is_already_batched(self, is_already_batched: bool) -> None:
        self._is_already_batched = is_already_batched

    def is_already_batched(self) -> bool:
        return self._is_already_batched

    def is_batched(self) -> bool:
        return self._is_batched

    def get_collider(self) -> Collider | None:
        return self._collider

    def get_sprite(self) -> Sprite or Surface:
        return self._sprite

    def set_sprite(self, sprite: Sprite | Surface) -> None:
        if self.is_batched() and not isinstance(sprite, Surface):
            raise ValueError("Sprite must be a Surface")
        if not self.is_batched() and not isinstance(sprite, Sprite):
            raise ValueError("Sprite must be a Sprite")
        self._sprite = sprite

    def get_transform(self) -> Transform:
        return self._transform

    def set_transform(self, transform: Transform) -> None:
        self._transform = transform

    def get_physics(self) -> Physics | None:
        return self._physics

    def set_physics(self, physics: Physics) -> None:
        self._physics = physics

    def has_collider(self) -> bool:
        return self._has_collider

    def shows_debug_collider(self) -> bool:
        return self._collider_debug_show

    def shows_debug_transform(self) -> bool:
        return self._transform_debug_show

    def shows_debug_forward(self) -> bool:
        return self._forward_debug_show

    def debug_config_show_transform(self) -> None:
        self._transform_debug_show = True

    def debug_config_show_collider(self) -> None:
        self._collider_debug_show = True

    def debug_config_show_forward(self) -> None:
        self._forward_debug_show = True

    def debug_config_hide_transform(self) -> None:
        self._transform_debug_show = False

    def debug_config_hide_collider(self) -> None:
        self._collider_debug_show = False

    def debug_config_hide_forward(self) -> None:
        self._forward_debug_show = False

    def set_layer(self, render_layer: RenderLayer):
        self._sprite.layer = render_layer.value

    def get_fitness(self) -> float:
        return self.fitness

    def set_fitness(self, fitness: float) -> None:
        self.fitness = fitness
