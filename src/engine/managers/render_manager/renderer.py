"""
This module contains the Renderer and DebugRenderer classes that are used to render the game.
"""
from typing import Optional

import pygame
from numpy import ndarray
from pygame import Vector2, Surface

from src.engine.components.collider import Collider
from src.engine.components.sprite import Sprite
from src.engine.components.transform import Transform
from src.engine.engine_attributes import EngineAttributes
from src.engine.engine_fonts import EngineFonts
from src.engine.managers.render_manager.background_batch import BackgroundBatch
from src.engine.managers.render_manager.render_layers import RenderLayer
from src.engine.managers.window_manager.window import Window
from src.game.camera_coordinates import apply_view_to_rect, apply_view_to_pos, CameraCoords


class DebugRenderer:
    """
    DebugRenderer class that manages the rendering of debug information for the engine.
    This also holds the information whether the engine is in debug mode or not (regarding rendering).
    If the engine is in debug mode, it will render debug information, otherwise it will not.
    """

    def __init__(self, window: Window):
        self.window: Window = window
        self.debug_mode: bool = False

    def draw_collider(self, collider: Collider) -> None:
        """
        Draw the collider of an entity.
        This receives a collider and draws a rectangle around it.
        :param collider: A Collider object
        :return: None
        """
        if collider is None:
            raise ValueError("Collider cannot be None")
        if not collider.is_active() or not collider.shows_debug_collider():
            return
        self.draw_rect_absolute(collider.rect, EngineAttributes.COLLIDER_COLOR_RECT,
                                EngineAttributes.FORWARD_LINE_THICKNESS)

    def disable_debug_mode(self) -> None:
        """
        This method sets the debug mode to False.
        :return:
        """
        self.debug_mode = False

    def enable_debug_mode(self) -> None:
        """
        This method sets the debug mode to True.
        :return:
        """
        self.debug_mode = True

    def draw_transform(self, transform: Transform) -> None:
        """
        This method is in charge of drawing the transform information of an entity as text on the screen.
        It will draw it at the position of the entity.
        :param transform:
        :return:
        """
        if transform is None:
            raise ValueError("Transform cannot be None")
        if not transform.shows_debug_transform():
            return

        position = transform.get_position()
        # rotation = transform.get_rotation()
        # scale = transform.get_scale()

        # Format position, rotation, and scale with two decimal places
        position_text = f"({position[0]:.2f}, {position[1]:.2f})"

        self.draw_text(position_text, position)
        # self.draw_text(rotation_text, Vector2(position[0], position[1] + 15))
        # self.draw_text(scale_text, Vector2(position[0], position[1] + 30))

        self.draw_circle(position.copy(), 4,
                         (255, 255, 255), EngineAttributes.FORWARD_LINE_THICKNESS)

    def draw_forward_vector(self, transform: Transform) -> None:
        """
        This method is in charge of drawing the forward vector of an entity as a line on the screen.
        It will draw it from the position of the entity to the vector forward multiplied by a line length.
        :param transform:
        :return:
        """
        if transform is None:
            raise ValueError("Transform cannot be None")
        if not transform.shows_debug_forward():
            return

        forward_vector = transform.get_forward()
        position = transform.get_position().copy()

        # Scale the forward vector by the desired line length
        scaled_forward_vector = forward_vector * EngineAttributes.FORWARD_LINE_LENGTH

        # Calculate the endpoint of the line
        end_position = position + scaled_forward_vector

        # Draw the line from the entity's position to the calculated endpoint
        self.draw_line(position, end_position, EngineAttributes.FORWARD_LINE_COLOR,
                       EngineAttributes.FORWARD_LINE_THICKNESS)

    def draw_rect(self, rect: pygame.Rect, color: tuple[int, int, int] = (255, 0, 0), thickness: int = 1) -> None:
        """
        Draw a rectangle on the screen.
        It will draw relative to the camera position.
        :param rect: The rectangle to draw
        :param color: The color of the rectangle
        :param thickness: The thickness of the rectangle
        :return: None
        """
        apply_view_to_rect(rect, CameraCoords.get_camera_position())
        pygame.draw.rect(self.window.get_window(), color, rect, thickness)

    def draw_rect_absolute(self, rect: pygame.Rect, color: tuple[int, int, int] = (255, 0, 0),
                           thickness: int = 1) -> None:
        """
        Draw a rectangle on the screen.
        It will draw in absolute position in the screen.
        :param rect: The rectangle to draw
        :param color: The color of the rectangle
        :param thickness: The thickness of the rectangle
        :return: None
        """
        pygame.draw.rect(self.window.get_window(), color, rect, thickness)

    def draw_polygon(self, points: ndarray, color: tuple[int, int, int], thickness: int = 1) -> None:
        """
        Draw a polygon on the screen.
        It will draw relative to the camera position.
        :param points: Set of points to draw the polygon
        :param color: The color of the polygon lines
        :param thickness: The thickness of the polygon lines
        :return: None
        """
        for i in range(len(points)):
            points[i] = apply_view_to_pos(points[i][0], points[i][1], CameraCoords.get_camera_position().x,
                                          CameraCoords.get_camera_position().y)
        pygame.draw.polygon(self.window.get_window(), color, points, width=thickness)

    def draw_line(self, start_pos: Vector2, end_pos: Vector2, color: tuple[int, int, int], thickness: int = 1) -> None:
        """
        Draw a line on the screen.
        It will draw relative to the camera position.
        :param start_pos: The starting position of the line
        :param end_pos: The ending position of the line
        :param color: The color of the line
        :param thickness: The thickness of the line
        :return: None
        """
        start_pos.update(apply_view_to_pos(start_pos.x, start_pos.y, CameraCoords.get_camera_position().x,
                                           CameraCoords.get_camera_position().y))
        end_pos.update(
            apply_view_to_pos(end_pos.x, end_pos.y, CameraCoords.get_camera_position().x,
                              CameraCoords.get_camera_position().y))
        pygame.draw.line(self.window.get_window(), color, start_pos, end_pos, thickness)

    def draw_circle(self, center: Vector2, radius: int, color: tuple[int, int, int] = (255, 0, 0),
                    thickness: int = 1) -> None:
        """
        Draw a circle on the screen.
        It will draw relative to the camera position.
        :param center: The center of the circle
        :param radius: The radius of the circle
        :param color: The color of the circle line
        :param thickness: The thickness of the circle line
        :return:
        """
        center.update(
            apply_view_to_pos(center.x, center.y, CameraCoords.get_camera_position().x,
                              CameraCoords.get_camera_position().y))
        pygame.draw.circle(self.window.get_window(), color, center, radius, width=thickness)

    def draw_circle_absolute(self, center: Vector2, radius: int, color: tuple[int, int, int] = (255, 0, 0),
                             thickness: int = 1) -> None:
        """
        Draw a circle on the screen.
        It will draw in absolute position in the screen.
        :param center: Center of the circle
        :param radius: Radius of the circle
        :param color: Color of the circle line
        :param thickness: Thickness of the circle line
        :return: None
        """
        pygame.draw.circle(self.window.get_window(), color, center, radius, width=thickness)

    def draw_text(self, text: str, position: Vector2, color: tuple[int, int, int] = EngineAttributes.DEBUG_FONT_COLOR,
                  centered: bool = False) -> None:
        """
        Draw text on the screen.
        It will draw relative to the camera position.
        :param text: The text to draw
        :param position: The position of the text
        :param color: The color of the text
        :param centered: If the text should be centered
        :return: None
        """
        text_surface = EngineFonts.get_fonts().debug_entity_font.render(text, True, color)
        pos = position.copy()
        pos.update(
            apply_view_to_pos(pos.x, pos.y, CameraCoords.get_camera_position().x,
                              CameraCoords.get_camera_position().y))

        self.window.get_window().blit(text_surface, text_surface.get_rect(center=pos) if centered else pos)

    def draw_text_absolute(self, text: str, position: Vector2,
                           color: tuple[int, int, int] = EngineAttributes.DEBUG_FONT_COLOR) -> None:
        """
        Draw text on the screen.
        It will draw in absolute position in the screen.
        :param text: The text to draw
        :param position: The position of the text
        :param color: The color of the text
        :return: None
        """
        text_surface = EngineFonts.get_fonts().debug_entity_font.render(text, True, color)
        self.window.get_window().blit(text_surface, position)


class Renderer:
    """
    This is the Renderer class that manages the rendering of the engine.
    This will draw the background batch, the sprites and text or other interface elements.
    It is also in charge of updating the sprites and the background batch.
    """
    def __init__(self, window: Window):
        self.window = window
        self.sprite_group = pygame.sprite.LayeredUpdates()
        self.surface_batch = pygame.surface.Surface((self.window.get_width(), self.window.get_height()))
        self.surface_batch_position: Vector2 = Vector2(0, 0)
        self.surface_batch_dirty: bool = False
        self.background_batch: Optional[BackgroundBatch] = None
        self.camera_pos = Vector2(0, 0)

    def render(self) -> None:
        """
        This method is in charge of rendering the sprites and the background batch.
        It will call the update method of the sprite group and draw the sprites.
        And will draw the background batch if it exists.
        :return:
        """
        self.sprite_group.update()
        if self.background_batch is not None:
            self.surface_batch.blit(self.background_batch.get_batch_surface(),
                                    apply_view_to_pos(0, int(self.surface_batch.get_height() * 1.5),
                                                      CameraCoords.get_camera_position().x,
                                                      CameraCoords.get_camera_position().y))
        self.window.get_window().blit(self.surface_batch, (0, 0))
        self.sprite_group.draw(self.window.get_window())
        self.surface_batch.fill(EngineAttributes.BACKGROUND_COLOR)

    def update(self, sprite: Sprite, transform: Transform, is_batched: bool, layer: RenderLayer) -> None:
        """
        This method is in charge of updating the sprite and adding it to the renderer.
        Updating the sprite means updating the transform and adding it to the sprite group.
        If the sprite is batched, it will not be added to the sprite group, only the background batch.
        :param sprite: The sprite to update
        :param transform: The transform of the sprite
        :param is_batched: If the sprite is batched
        :param layer: The layer of the sprite
        :return: None
        """
        assert sprite is not None, "Sprite cannot be None"
        assert transform is not None, "Transform cannot be None"

        if is_batched:
            return

        # Update the sprite's transform
        sprite.update_transform(transform, CameraCoords.get_camera_position())
        self.surface_batch_position = -CameraCoords.get_camera_position()
        # Add the sprite to the renderer if it hasn't been added yet
        if not sprite.is_added_to_renderer() and not is_batched:
            # noinspection PyTypeChecker
            self.sprite_group.add(sprite, layer=layer.value)
            # Mark the sprite as added to the renderer, so we don't add it again
            sprite.set_added_to_renderer()

    def create_background_batch(self, batch_sprites: list[Surface], batch_transforms: list[Transform]) -> None:
        """
        This method is in charge of creating the background batch.
        This takes the batch sprites and transforms and creates a BackgroundBatch object.
        :param batch_sprites:
        :param batch_transforms:
        :return:
        """
        entity_width = batch_sprites[0].get_width()
        entity_height = batch_sprites[0].get_height()
        self.background_batch = BackgroundBatch(entity_width, entity_height, batch_sprites, batch_transforms)

    def draw_surface(self, surface: pygame.Surface, position: Vector2) -> None:
        """
        Draw a surface on the screen at a given position.
        :param surface: The surface to draw
        :param position: The position to draw the surface
        :return: None
        """
        self.window.get_window().blit(surface, position)

    def draw_text(self, text: str, position: Vector2, color: tuple[int, int, int] = EngineAttributes.DEBUG_FONT_COLOR,
                  size: int = EngineAttributes.DEBUG_ENTITY_FONT_SIZE):
        """
        Draw text on the screen.
        It will draw relative to the camera position.
        :param text: The text to draw
        :param position: The position of the text
        :param color: The color of the text
        :param size: The size of the text in pixels
        :return: None
        """
        current_font = pygame.font.SysFont(EngineAttributes.DEBUG_FONT, size)
        text_surface = current_font.render(text, True, color)
        pos = position.copy()
        pos.update(
            apply_view_to_pos(pos.x, pos.y,
                              CameraCoords.get_camera_position().x,
                              CameraCoords.get_camera_position().y))
        self.window.get_window().blit(text_surface, pos)

    def draw_text_absolute(self, text: str, position: Vector2,
                           color: tuple[int, int, int] = EngineAttributes.DEBUG_FONT_COLOR,
                           size: int = EngineAttributes.DEBUG_ENTITY_FONT_SIZE, centered: bool = False,
                           bold: bool = False):
        """
        Draw text on the screen.
        It will draw in absolute position in the screen.
        :param text: The text to draw
        :param position: The position of the text
        :param color: The color of the text
        :param size: The size of the text in pixels
        :param centered: If the text should be centered
        :param bold: If the text should be bold
        :return: None
        """
        current_font = pygame.font.SysFont(EngineAttributes.DEBUG_FONT, size, bold=bold)
        text_surface = current_font.render(text, True, color)
        self.window.get_window().blit(text_surface, text_surface.get_rect(center=position) if centered else position)

    def draw_rect_absolute(self, rect: pygame.Rect, color: tuple[int, int, int] = (255, 0, 0),
                           thickness: int = 1) -> None:
        """
        Draw a rectangle on the screen.
        It will draw in absolute position in the screen.
        :param rect: The rectangle to draw
        :param color: The color of the rectangle
        :param thickness: The thickness of the rectangle
        :return: None
        """
        pygame.draw.rect(self.window.get_window(), color, rect, thickness)

    def draw_image_absolute(self, image: pygame.Surface, position: Vector2) -> None:
        """
        Draw an image on the screen.
        It will draw in absolute position in the screen.
        :param image: The image to draw
        :param position: The position of the image
        :return: None
        """
        self.window.get_window().blit(image, position)

    def draw_circle_absolute(self, center: Vector2, radius: int, color: tuple[int, int, int] = (255, 0, 0),
                             thickness: int = 1) -> None:
        """
        Draw a circle on the screen.
        It will draw in absolute position in the screen.
        :param center: Center of the circle
        :param radius: Radius of the circle
        :param color: Color of the circle line
        :param thickness: Thickness of the circle line
        :return: None
        """
        pygame.draw.circle(self.window.get_window(), color, center, radius, width=thickness)

    def render_clear(self) -> None:
        """
        Completely clear the renderer.
        This will set all the data structures to empty and will clear the surface batch.
        :return:
        """
        self.sprite_group = pygame.sprite.LayeredUpdates()
        self.background_batch = None
        self.surface_batch_position: Vector2 = Vector2(0, 0)
        self.surface_batch_dirty: bool = False
        self.camera_pos = Vector2(0, 0)
