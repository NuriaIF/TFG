from pygame import Vector2

from engine.components.collider import Collider
from engine.components.transform import Transform
from engine.engine_attributes import EngineAttributes
from engine.engine_fonts import EngineFonts
from engine.fps_manager import FPSManager
from engine.managers.collider_manager.collider_manager import ColliderManager
from engine.managers.entity_manager.entity_manager import EntityManager
from engine.managers.input_manager.input_manager import InputManager
from engine.managers.input_manager.key import Key
from engine.managers.physics_manager.physics_manager import PhysicsManager
from engine.managers.render_manager.renderer import Renderer, DebugRenderer
from engine.managers.sound_manager.sound_manager import SoundManager
from engine.managers.window_manager.window_manager import Window
from game.camera import Camera


class Engine:
    def __init__(self):
        self.window = Window("Game", 1200, 800, fullscreen=True)
        self.input_manager = InputManager()
        self.renderer = Renderer(self.window)
        self.debug_renderer = DebugRenderer(self.window)
        self.physics_manager = PhysicsManager()
        self.sound_manager = SoundManager()
        self.engine_fonts = EngineFonts()
        self.collider_manager = ColliderManager()
        self.camera = Camera(Vector2(self.window.get_width(), self.window.get_height()))
        self.entity_manager = EntityManager()
        self.background_batch_created = False

    def handle_engine_inputs(self):
        if self.input_manager.is_key_down(Key.K_O):
            self.debug_renderer.enable_debug_mode()
        if self.input_manager.is_key_down(Key.K_P):
            self.debug_renderer.disable_debug_mode()

    def update(self, delta_time: float):
        self.input_manager.update()
        self.handle_engine_inputs()

        self.camera.update(delta_time)

        batch_sprites = []
        batch_transforms = []

        self.renderer.set_camera_position(self.camera.get_position())
        self.debug_renderer.set_camera_position(self.camera.get_position())
        for entity in self.entity_manager.entities:
            # Getting the next frame collider before updating the physics
            # This way a collider never enters another, blocking the entity
            transform = self.entity_manager.get_transform(entity)
            physics = self.entity_manager.get_physics(entity)
            sprite = self.entity_manager.get_sprite(entity)
            collider = self.entity_manager.get_collider(entity)

            if collider.is_active():
                sprite_rect = self.entity_manager.get_sprite_rect(entity)
                next_frame_transform: Transform = \
                    self.physics_manager.get_next_transform_and_physics(transform, physics, delta_time)[0]
                next_frame_collider: Collider = Collider(
                    self.entity_manager.get_rect_with_transform(entity, next_frame_transform))
                self.collider_manager.update(collider, sprite_rect, physics, transform, next_frame_collider)

            if not physics.is_static():
                self.physics_manager.update(entity, physics, transform, self.entity_manager, delta_time)

            is_batched = self.entity_manager.is_batched(entity)
            layer = self.entity_manager.get_layer(entity)
            self.renderer.update(sprite, transform, is_batched, layer)

            if is_batched:
                batch_transforms.append(transform)
                batch_sprites.append(sprite)

        if not self.background_batch_created:
            self.renderer.create_background_batch(batch_sprites, batch_transforms)
            self.background_batch_created = True

    def draw_fps(self):
        self.renderer.draw_surface(
            EngineFonts.get_fonts().debug_UI_font.render(f"FPS: {round(FPSManager.get_average_fps(), 2)}", True,
                                                         EngineAttributes.DEBUG_FONT_COLOR), Vector2(0, 0))

    def draw_camera_position(self):
        self.renderer.draw_surface(
            EngineFonts.get_fonts().debug_UI_font.render(f"Camera Position: {self.camera.get_position()}", True,
                                                         EngineAttributes.DEBUG_FONT_COLOR), Vector2(0, 20))

    def draw_entity_debug_information(self):
        for entity in self.entity_manager.entities:
            collider = self.entity_manager.get_collider(entity)
            transform = self.entity_manager.get_transform(entity)
            self.debug_renderer.render_debug_information(collider, transform)

    def render(self):
        self.window.clear()
        self.renderer.render()

        self.draw_fps()

        self.game_render()

        # Fast return if debug mode is disabled, no need to render debug information
        if self.debug_renderer.debug_mode is False:
            self.window.swap_buffers()
            return
        self.draw_entity_debug_information()
        self.window.swap_buffers()

    def game_render(self):
        pass

    def game_render_debug(self):
        pass

    def create_entity(self, sprite_path: str, has_collider: bool = False, background_batched: bool = False,
                      is_static: bool = True, is_training: bool = False) -> int:
        entity_id = self.entity_manager.add_entity(sprite_path, has_collider=has_collider, batched=background_batched,
                                                   is_static=is_static, is_training=is_training)
        return entity_id

    def play_music(self, file_name: str) -> None:
        self.sound_manager.play_music(file_name)

    def play_sound(self, file_name: str) -> None:
        self.sound_manager.play_sound(file_name)
