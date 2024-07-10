"""
The module contains the EntityManager class, which is responsible for managing the entities in the game.
"""
from typing import Union

import pygame
from pygame import Surface

from src.engine.components.collider import Collider
from src.engine.components.physics import Physics
from src.engine.components.sprite import Sprite
from src.engine.components.transform import Transform
from src.engine.managers.render_manager.render_layers import RenderLayer
from src.engine.managers.resource_manager.sprite_loader import SpriteLoader


class EntityManager:
    """
    The entity manager is a container for all the entities in the game. It holds the components of the entities and
    provides methods to access and modify the components of the entities.

    This is useful to keep all the entities and their components in one place, and to have a single point of access to
    the entities.

    Also, it stores the components in separate arrays instead of storing them in the entity class itself. This is
    because it is more efficient to store the components in separate arrays, as it allows for better cache locality.
    """
    def __init__(self):
        self.entities: list[int] = []

        self.transforms: list[Transform] = []
        self.physics: list[Physics] = []
        self.sprites: list[Union[Sprite, Surface]] = []
        self.colliders: list[Collider] = []

        self.sprite_rects: list[pygame.Rect] = []
        self.next_frame_sprite_rects: list[pygame.Rect] = []

        self.batched: list[bool] = []
        self.layers: list[RenderLayer] = []

        self.next_entity_id: int = 0

    def create_entity(self, sprite_path: str, has_collider: bool = False, batched: bool = False,
                      is_static: bool = True) -> int:
        """
        Method that creates and entity with all the necessary components.
        Acts like a factory method for entities.
        :param sprite_path: The path to the sprite of the entity
        :param has_collider: Whether the entity has a collider or not
        :param batched: Whether the sprite is batched or not
        :param is_static: Whether the entity is static or not
        :return: The id of the created entity
        """
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

    def get_transform(self, entity_id: int) -> Transform:
        """
        Get the transform component of the entity
        :param entity_id: The id of
        :return: The transform component of the entity
        """
        return self.transforms[entity_id]

    def get_physics(self, entity_id: int) -> Physics:
        """
        Get the physics component of the entity
        :param entity_id: The id of the entity
        :return: The physics component of the entity
        """
        return self.physics[entity_id]

    def get_sprite(self, entity_id: int) -> Union[Sprite, Surface]:
        """
        Get the sprite component of the entity
        :param entity_id: The id of the entity
        :return: The sprite component of the entity
        """
        return self.sprites[entity_id]

    def get_collider(self, entity_id: int) -> Collider:
        """
        Get the collider component of the entity
        :param entity_id: The id of the entity
        :return: The collider component of the entity
        """
        return self.colliders[entity_id]

    def get_layer(self, entity_id: int) -> RenderLayer:
        """
        Get the render layer of the entity
        :param entity_id: The id of the entity
        :return: The render layer of the entity
        """
        return self.layers[entity_id]

    def is_batched(self, entity_id: int) -> bool:
        """
        Check if the entity is batched
        :param entity_id: The id of the entity
        :return: True if the entity is batched, False otherwise
        """
        return self.batched[entity_id]

    def set_layer(self, entity_id: int, layer: RenderLayer) -> None:
        """
        Set the render layer of the entity
        :param entity_id: The id of the entity
        :param layer: The render layer to set
        :return: None
        """
        self.layers[entity_id] = layer

    def get_sprite_rect(self, entity_id: int) -> pygame.Rect:
        """
        Get the rect of the sprite of the entity
        :param entity_id: The id of the entity
        :return: The rect of the sprite of the entity
        """
        if self.batched[entity_id]:
            position = self.get_transform(entity_id).get_position()
            rect = self.sprite_rects[entity_id]
            rect.x = position.x
            rect.y = position.y
            return rect

        sprite = self.get_sprite(entity_id)
        return sprite.rect

    def get_next_frame_sprite_rect(self, entity_id: int) -> pygame.Rect:
        """
        Get the rect of the sprite of the entity for the next frame
        This is useful for collision detection
        :param entity_id: The id of the entity
        :return: The rect of the sprite of the entity for the next frame
        """
        return self.next_frame_sprite_rects[entity_id]

    def get_rect_with_transform(self, entity_id: int, transform: Transform) -> pygame.Rect:
        """
        Get the rect of the sprite of the entity with the given transform
        :param entity_id: The id of the entity
        :param transform: The transform to use
        :return: The rect of the sprite of the entity with the given transform
        """
        position = transform.get_position()
        rect = self.get_next_frame_sprite_rect(entity_id)
        rect.x = position.x
        rect.y = position.y

        return rect

    def set_transform(self, entity: int, updated_transform: Transform) -> None:
        """
        Set the transform of the entity
        :param entity:
        :param updated_transform:
        :return: None
        """
        self.transforms[entity] = updated_transform

    def set_physics(self, entity: int, updated_physics: Physics) -> None:
        """
        Set the physics of the entity
        :param entity:
        :param updated_physics:
        :return:  None
        """
        self.physics[entity] = updated_physics

    def reset_entity(self, entity_id) -> None:
        """
        Resets all the values of an entity to default
        :param entity_id: The id of the entity
        :return: None
        """
        self.get_transform(entity_id).reset()
        self.get_physics(entity_id).reset()
        self.get_collider(entity_id).reset()

    def clear(self) -> None:
        """
        Clear all the entities and their components, setting the entity manager to its initial state
        :return: None
        """
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

