import pygame
from numpy import ndarray
from pygame import Vector2

from engine.components.collider import Collider
from engine.components.sprite import Sprite
from engine.components.transform import Transform
from engine.engine_attributes import EngineAttributes
from engine.engine_fonts import EngineFonts
from engine.managers.render_manager.background_batch import BackgroundBatch
from engine.managers.render_manager.render_layers import RenderLayer
from engine.managers.window_manager.window_manager import Window
from game.camera_coordinates import apply_view_to_rect, apply_view_to_pos, CameraCoords


class DebugRenderer:
    def __init__(self, window: Window):
        self.window: Window = window
        self.debug_mode: bool = False
        self.camera_pos: Vector2 = Vector2(0, 0)

    def set_camera_position(self, camera_pos: Vector2) -> None:
        self.camera_pos = camera_pos

    def draw_collider(self, collider: Collider) -> None:
        if collider is None:
            raise ValueError("Collider cannot be None")
        if not collider.is_active() or not collider.shows_debug_collider():
            return
        self.draw_rect_absolute(collider.rect, EngineAttributes.COLLIDER_COLOR_RECT,
                                EngineAttributes.FORWARD_LINE_THICKNESS)

    def disable_debug_mode(self) -> None:
        self.debug_mode = False

    def enable_debug_mode(self) -> None:
        self.debug_mode = True

    def draw_transform(self, transform: Transform) -> None:
        if transform is None:
            raise ValueError("Transform cannot be None")
        if not transform.shows_debug_transform():
            return

        position = transform.get_position()
        rotation = transform.get_rotation()
        scale = transform.get_scale()

        # Format position, rotation, and scale with two decimal places
        position_text = f"({position[0]:.2f}, {position[1]:.2f})"
        rotation_text = f"Rotation: {rotation:.2f}"
        scale_text = f"Scale: ({scale[0]:.2f}, {scale[1]:.2f})"

        self.draw_text(position_text, position.copy())
        # self.draw_text(rotation_text, Vector2(position[0], position[1] + 15))
        # self.draw_text(scale_text, Vector2(position[0], position[1] + 30))

        self.draw_circle(position.copy(), 4,
                         (255, 255, 255), EngineAttributes.FORWARD_LINE_THICKNESS)

    def draw_forward_vector(self, transform: Transform) -> None:
        if transform is None:
            raise ValueError("Transform cannot be None")
        if not transform.shows_debug_forward():
            return

        forward_vector = transform.get_forward()
        position = transform.get_position().copy()

        # Define a scale for how long you want the forward vector line to be
        line_length = 50

        # Scale the forward vector by the desired line length
        scaled_forward_vector = forward_vector * line_length

        # Calculate the endpoint of the line
        end_position = position + scaled_forward_vector

        # Draw the line from the entity's position to the calculated endpoint
        self.draw_line(position, end_position, EngineAttributes.FORWARD_LINE_COLOR,
                       EngineAttributes.FORWARD_LINE_THICKNESS)

    def draw_rect(self, rect: pygame.Rect, color: tuple[int, int, int] = (255, 0, 0), thickness: int = 1) -> None:
        apply_view_to_rect(rect, CameraCoords.get_camera_position())
        pygame.draw.rect(self.window.get_window(), color, rect, thickness)

    def draw_rect_absolute(self, rect: pygame.Rect, color: tuple[int, int, int] = (255, 0, 0),
                           thickness: int = 1) -> None:
        pygame.draw.rect(self.window.get_window(), color, rect, thickness)

    def draw_polygon(self, points: ndarray, color: tuple[int, int, int], thickness: int = 1) -> None:
        for i in range(len(points)):
            points[i] = apply_view_to_pos(points[i][0], points[i][1], CameraCoords.get_camera_position().x,
                                          CameraCoords.get_camera_position().y)
        pygame.draw.polygon(self.window.get_window(), color, points, width=thickness)

    def draw_line(self, start_pos: Vector2, end_pos: Vector2, color: tuple[int, int, int], thickness: int = 1) -> None:
        start_pos.update(apply_view_to_pos(start_pos.x, start_pos.y, CameraCoords.get_camera_position().x,
                                           CameraCoords.get_camera_position().y))
        end_pos.update(
            apply_view_to_pos(end_pos.x, end_pos.y, CameraCoords.get_camera_position().x,
                              CameraCoords.get_camera_position().y))
        pygame.draw.line(self.window.get_window(), color, start_pos, end_pos, thickness)

    def draw_circle(self, center: Vector2, radius: int, color: tuple[int, int, int] = (255, 0, 0),
                    thickness: int = 1) -> None:
        center.update(
            apply_view_to_pos(center.x, center.y, CameraCoords.get_camera_position().x,
                              CameraCoords.get_camera_position().y))
        pygame.draw.circle(self.window.get_window(), color, center, radius, width=thickness)

    def draw_circle_absolute(self, center: Vector2, radius: int, color: tuple[int, int, int] = (255, 0, 0),
                             thickness: int = 1) -> None:
        pygame.draw.circle(self.window.get_window(), color, center, radius, width=thickness)

    def draw_text(self, text: str, position: Vector2, color: tuple[int, int, int] = EngineAttributes.DEBUG_FONT_COLOR):
        text_surface = EngineFonts.get_fonts().debug_entity_font.render(text, True, color)
        position.update(
            apply_view_to_pos(position.x, position.y, CameraCoords.get_camera_position().x,
                              CameraCoords.get_camera_position().y))
        self.window.get_window().blit(text_surface, position)

    def draw_text_absolute(self, text: str, position: Vector2,
                           color: tuple[int, int, int] = EngineAttributes.DEBUG_FONT_COLOR):
        text_surface = EngineFonts.get_fonts().debug_entity_font.render(text, True, color)
        self.window.get_window().blit(text_surface, position)


class Renderer:

    def __init__(self, window: Window):
        self.window = window
        self.sprite_group = pygame.sprite.LayeredUpdates()
        self.surface_batch = pygame.surface.Surface((self.window.get_width(), self.window.get_height()))
        self.surface_batch_position: Vector2 = Vector2(0, 0)
        self.surface_batch_dirty: bool = False
        self.background_batch: BackgroundBatch | None = None
        self.camera_pos = Vector2(0, 0)

    def render(self) -> None:
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
        assert sprite is not None, "Sprite cannot be None"
        assert transform is not None, "Transform cannot be None"

        if is_batched:
            return

        # Update the sprite's transform
        sprite.update_transform(transform, CameraCoords.get_camera_position())
        self.surface_batch_position = -CameraCoords.get_camera_position()
        # Add the sprite to the renderer if it hasn't been added yet
        if not sprite.is_added_to_renderer() and not is_batched:
            self.sprite_group.add(sprite, layer=layer.value)
            # Mark the sprite as added to the renderer, so we don't add it again
            sprite.set_added_to_renderer()

    def create_background_batch(self, batch_sprites, batch_transforms) -> None:
        entity_width = batch_sprites[0].get_width()
        entity_height = batch_sprites[0].get_height()
        self.background_batch = BackgroundBatch(entity_width, entity_height, batch_sprites, batch_transforms)

    def draw_surface(self, surface: pygame.Surface, position: Vector2):
        self.window.get_window().blit(surface, position)

    def draw_text(self, text: str, position: Vector2, color: tuple[int, int, int] = EngineAttributes.DEBUG_FONT_COLOR,
                  size: int = EngineAttributes.DEBUG_ENTITY_FONT_SIZE):
        current_font = pygame.font.SysFont(EngineAttributes.DEBUG_FONT, size, bold=False)
        text_surface = current_font.render(text, True, color)
        position.update(
            apply_view_to_pos(position.x, position.y,
                              CameraCoords.get_camera_position().x,
                              CameraCoords.get_camera_position().y))
        self.window.get_window().blit(text_surface, position)

    def draw_text_absolute(self, text: str, position: Vector2,
                           color: tuple[int, int, int] = EngineAttributes.DEBUG_FONT_COLOR,
                           size: int = EngineAttributes.DEBUG_ENTITY_FONT_SIZE):
        current_font = pygame.font.SysFont(EngineAttributes.DEBUG_FONT, size, bold=False)
        text_surface = current_font.render(text, True, color)
        self.window.get_window().blit(text_surface, position)
