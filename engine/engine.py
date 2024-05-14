from pygame import Vector2

from engine.engine_attributes import EngineAttributes
from engine.engine_fonts import EngineFonts
from engine.entities.entity import Entity
from engine.fps_manager import FPSManager
from engine.managers.collider_manager.collider_manager import ColliderManager
from engine.managers.input_manager.input_manager import InputManager
from engine.managers.input_manager.key import Key
from engine.managers.physics_manager.physics_manager import PhysicsManager
from engine.managers.render_manager.renderer import Renderer
from engine.managers.sound_manager.sound_manager import SoundManager
from engine.managers.window_manager.window_manager import Window
from game.camera import Camera


class Engine:
    def __init__(self):
        self.window = Window("Game", 1200, 800, fullscreen=True)
        self.input_manager = InputManager()
        self.renderer = Renderer(self.window)
        self.physics_manager = PhysicsManager()
        self.sound_manager = SoundManager()
        self.engine_fonts = EngineFonts()
        self.collider_manager = ColliderManager()
        self.camera = Camera(Vector2(self.window.get_width(), self.window.get_height()))
        self.entities: list[Entity] = []

    def update(self, delta_time: float):
        self.input_manager.update()
        if self.input_manager.is_key_down(Key.K_O):
            self.renderer.enable_debug_mode()
        if self.input_manager.is_key_down(Key.K_P):
            self.renderer.disable_debug_mode()
        self.camera.update(delta_time, self.entities)
        self.renderer.update_background_batch(self.camera.get_displacement())

        for entity in self.entities:
            if not entity.is_static():
                self.physics_manager.update(entity, delta_time)

            if entity.has_collider():
                self.collider_manager.update(entity, delta_time)

            self.renderer.update(entity)

    def render(self):
        self.window.clear()
        self.renderer.render_background_batch()
        self.renderer.render()

        if self.renderer.debug_mode is False:
            self.renderer.draw_surface(
                EngineFonts.get_fonts().debug_UI_font.render(f"FPS: {round(FPSManager.get_average_fps(), 2)}",
                                                             True, EngineAttributes.DEBUG_FONT_COLOR), Vector2(0, 0))
            self.game_render()
            self.window.swap_buffers()
            return
        self.renderer.draw_surface(
            EngineFonts.get_fonts().debug_UI_font.render(f"FPS: {round(FPSManager.get_average_fps(), 2)}",
                                                         True, EngineAttributes.DEBUG_FONT_COLOR), Vector2(0, 0))
        self.renderer.draw_surface(
            EngineFonts.get_fonts().debug_UI_font.render(f"Camera Position: {self.camera.get_position()}",
                                                         True, EngineAttributes.DEBUG_FONT_COLOR), Vector2(0, 20))
        for entity in self.entities:
            self.renderer.render_debug_information(entity)

        self.game_render_debug()

        self.window.swap_buffers()

    def game_render_debug(self):
        pass

    def create_entity(self, sprite_path: str, has_collider: bool = False, background_batched: bool = False,
                      is_static: bool = True, is_training: bool = False) -> Entity:
        if not isinstance(sprite_path, str):
            raise ValueError("Sprite path must be a string")
        entity = Entity(sprite_path, has_collider=has_collider, batched=background_batched, is_static=is_static,
                        is_training=is_training)
        self.entities.append(entity)
        return entity

    def play_music(self, file_name: str) -> None:
        self.sound_manager.play_music(file_name)

    def play_sound(self, file_name: str) -> None:
        self.sound_manager.play_sound(file_name)
