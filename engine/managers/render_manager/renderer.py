import pygame
from pygame import Vector2

from engine.engine_attributes import EngineAttributes
from engine.engine_fonts import EngineFonts
from engine.entities.entity import Entity
from engine.managers.render_manager.background_batch import BackgroundBatch
from engine.managers.window_manager.window_manager import Window


class Renderer:

    def __init__(self, window: Window):
        self.window = window
        self.sprite_group = pygame.sprite.LayeredUpdates()
        self.surface_batch = pygame.surface.Surface((self.window.get_width(), self.window.get_height()))
        self.surface_batch_scale: Vector2 = Vector2(1, 1)
        self.surface_batch_position: Vector2 = Vector2(0, 0)
        self.surface_batch_dirty: bool = False
        self.debug_mode = False
        self.background_batch = None

    def render(self) -> None:
        self.sprite_group.update()  # Ensure all sprites are updated
        self.sprite_group.draw(self.window.get_window())
        self.surface_batch.fill(EngineAttributes.BACKGROUND_COLOR)

    def update_background_batch(self, displacement: Vector2) -> None:
        if displacement is None:
            raise ValueError("Displacement cannot be None")
        self.surface_batch_position += displacement

    def render_background_batch(self) -> None:
        # Scale the surface with the scale
        self.window.get_window().blit(self.surface_batch, (0, 0))

    def render_debug_information(self, entity: Entity) -> None:
        self._draw_entity_collider(entity)
        self._draw_entity_transform_text(entity)
        self._draw_entity_forward_vector(entity)

    def get_background_batch(self):
        return self.surface_batch

    def enable_debug_mode(self) -> None:
        self.debug_mode = True

    def disable_debug_mode(self) -> None:
        self.debug_mode = False

    def update(self, entity: Entity) -> None:
        if entity is None:
            raise ValueError("Entity cannot be None")
        sprite = entity.get_sprite()
        transform = entity.get_transform()

        if sprite is None:
            raise ValueError("Sprite cannot be None")
        if transform is None:
            raise ValueError("Transform cannot be None")

        if entity.is_batched():
            # self.add_to_background_batch(entity)
            return

        # Update the sprite's transform
        sprite.update_transform(transform)

        # Add the sprite to the renderer if it hasn't been added yet
        if not sprite.is_added_to_renderer() and not entity.is_batched():
            self.sprite_group.add(sprite, layer=sprite.layer)
            # Mark the sprite as added to the renderer, so we don't add it again
            sprite.set_added_to_renderer()

    def update_background(self, entities: list[Entity]) -> None:
        entity_width = entities[0].get_sprite().get_width()
        entity_height = entities[0].get_sprite().get_height()
        start_position = entities[0].get_transform().get_position()
        if self.background_batch is None:
            self.background_batch = BackgroundBatch(entity_width, entity_height, entities)
            for entity in entities:
                self.add_to_background_batch(entity)
        self.background_batch.draw(self.surface_batch, start_position)

    def add_to_background_batch(self, entity: Entity) -> None:
        if entity is None:
            raise ValueError("Entity cannot be None")
        sprite = entity.get_sprite()
        transform = entity.get_transform()
        self.background_batch.add_entity(sprite, transform.get_position())
        # self.surface_batch.blit(sprite, transform.get_position())

    def _draw_entity_collider(self, entity: Entity) -> None:
        if entity is None:
            raise ValueError("Entity cannot be None")
        if not entity.has_collider() or not entity.shows_debug_collider():
            return

        # Draw the collider rect as a rectangular outline
        collider_rect: pygame.Rect = entity.get_collider().get_rect()
        self.draw_rect(collider_rect, EngineAttributes.COLLIDER_COLOR_RECT, thickness=2)

    def _draw_entity_transform_text(self, entity: Entity) -> None:
        if entity is None:
            raise ValueError("Entity cannot be None")
        if not entity.shows_debug_transform():
            return
        transform = entity.get_transform()
        position = transform.get_position()

        # Format position, rotation, and scale with two decimal places
        position_text = f"({position[0]:.2f}, {position[1]:.2f})"
        rotation_text = f"Rotation: {transform.get_rotation():.2f}"
        scale = transform.get_scale()
        scale_text = f"Scale: ({scale[0]:.2f}, {scale[1]:.2f})"
        fitness_text = f"Fitness: {entity.get_fitness()}"

        # self.draw_text(position_text, position)
        self.draw_text(rotation_text, Vector2(position[0], position[1] + 15))
        # self.draw_text(scale_text, Vector2(position[0], position[1] + 30))
        self.draw_text(fitness_text, Vector2(position[0], position[1] + 45))

    def _draw_entity_forward_vector(self, entity: Entity) -> None:
        if entity is None:
            raise ValueError("Entity cannot be None")
        if not entity.shows_debug_forward():
            return

        transform = entity.get_transform()
        forward_vector = transform.get_forward()
        position = transform.get_position()

        # Define a scale for how long you want the forward vector line to be
        line_length = 50

        # Scale the forward vector by the desired line length
        scaled_forward_vector = forward_vector * line_length

        # Calculate the endpoint of the line
        end_position = position + scaled_forward_vector

        # Draw the line from the entity's position to the calculated endpoint
        self.draw_line(position, end_position, EngineAttributes.FORWARD_LINE_COLOR,
                       EngineAttributes.FORWARD_LINE_THICKNESS)

    def draw_surface(self, surface: pygame.Surface, position: Vector2):
        self.window.get_window().blit(surface, position)

    def draw_text(self, text: str, position: Vector2, color: tuple[int, int, int] = EngineAttributes.DEBUG_FONT_COLOR):
        text_surface = EngineFonts.get_fonts().debug_entity_font.render(text, True, color)
        self.window.get_window().blit(text_surface, position)

    def draw_provisional_text(self, text: str, position: Vector2,
                              color: tuple[int, int, int] = EngineAttributes.DEBUG_FONT_COLOR,
                              size: int = EngineAttributes.DEBUG_ENTITY_FONT_SIZE):
        current_font = pygame.font.SysFont(EngineAttributes.DEBUG_FONT,
                                           size, bold=False)
        text_surface = current_font.render(text, True, color)
        self.window.get_window().blit(text_surface, position)

    def draw_rect(self, rect: pygame.Rect, color: tuple[int, int, int] = (255, 0, 0),
                  thickness: int = 1) -> None:
        if not isinstance(rect, pygame.Rect):
            raise ValueError("Rect must be a pygame.Rect")
        pygame.draw.rect(self.window.get_window(), color, rect, thickness)

    def draw_polygon(self, points: list[Vector2], color: tuple[int, int, int], thickness: int = 1) -> None:
        if not all(isinstance(point, Vector2) for point in points):
            raise ValueError("All points must be pygame.Vector2")
        pygame.draw.polygon(self.window.get_window(), color, points, width=thickness)

    def draw_line(self, start_pos: Vector2, end_pos: tuple[int, int], color: tuple[int, int, int],
                  thickness: int = 1) -> None:
        pygame.draw.line(self.window.get_window(), color, start_pos, end_pos, thickness)

    def draw_circle(self, center: Vector2, radius: int, color: tuple[int, int, int] = (255, 0, 0),
                    thickness: int = 1) -> None:
        if not isinstance(center, pygame.Vector2):
            raise ValueError("Center must be a Vector2")
        pygame.draw.circle(self.window.get_window(), color, center, radius, width=thickness)
