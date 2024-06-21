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
from engine.managers.render_manager.render_layers import RenderLayer
from engine.managers.render_manager.renderer import Renderer
from engine.managers.sound_manager.sound_manager import SoundManager
from engine.managers.window_manager.window_manager import Window
from game.camera import Camera

import multiprocessing
from multiprocessing import Pool


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
        self.entity_manager = EntityManager()
        self.background_batch_created = False

    def update(self, delta_time: float):
        self.input_manager.update()
        if self.input_manager.is_key_down(Key.K_O):
            self.renderer.enable_debug_mode()
        if self.input_manager.is_key_down(Key.K_P):
            self.renderer.disable_debug_mode()
        self.camera.update(delta_time)
        self.renderer.update_background_batch(self.camera.get_displacement())

        batch_sprites = []
        batch_transforms = []

        # with Pool(multiprocessing.cpu_count()) as pool:
        #     updated_entities = pool.map(self._update_entity_physics_and_collision, [(entity, delta_time) for entity in self.entities])
        # for entity in updated_entities:
        #     self.renderer.update(entity)
        for entity in self.entity_manager.entities:
            # Getting the next frame collider before updating the physics
            # This way a collider never enters another, blocking the entity
            transform = self.entity_manager.get_transform(entity)
            physics = self.entity_manager.get_physics(entity)
            sprite = self.entity_manager.get_sprite(entity)
            collider = self.entity_manager.get_collider(entity)
            self.camera.update_transform(transform)

            if collider.is_active():
                sprite_rect = self.entity_manager.get_sprite_rect(entity)
                next_frame_transform: Transform = self.physics_manager.get_next_transform_and_physics(
                    transform, physics, delta_time)[0]
                next_frame_collider: Collider = Collider(self.entity_manager.get_rect_with_transform(
                    entity, next_frame_transform))
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
        self.renderer.draw_background(batch_transforms[0].get_position())

    # def _update_entity_physics_and_collision(self, args):
    #     entity, delta_time = args
    #     # Getting the next frame collider before updating the physics
    #     next_frame_transform: Transform = self.physics_manager.get_next_transform_and_physics(entity, delta_time)[0]
    #     next_frame_collider: Collider = Collider(entity.get_rect_with_transform(next_frame_transform))
    #     if entity.has_collider():
    #         self.collider_manager.update(entity, next_frame_collider)
    # 
    #     if not entity.is_static():
    #         self.physics_manager.update(entity, delta_time)
    # 
    #     return entity

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
        for entity in self.entity_manager.entities:
            collider = self.entity_manager.get_collider(entity)
            transform = self.entity_manager.get_transform(entity)
            self.renderer.render_debug_information(collider, transform)

        self.game_render_debug()

        self.window.swap_buffers()

    def game_render(self):
        pass

    def game_render_debug(self):
        pass

    def create_entity(self, sprite_path: str, has_collider: bool = False, background_batched: bool = False,
                      is_static: bool = True, is_training: bool = False) -> int:
        # if not isinstance(sprite_path, str):
        #     raise ValueError("Sprite path must be a string")
        # entity = Entity(sprite_path, has_collider=has_collider, batched=background_batched, is_static=is_static,
        #                 is_training=is_training)
        # self.entities.append(entity)
        entity_id = self.entity_manager.add_entity(sprite_path, has_collider=has_collider, batched=background_batched,
                                                   is_static=is_static, is_training=is_training)
        return entity_id

    def play_music(self, file_name: str) -> None:
        self.sound_manager.play_music(file_name)

    def play_sound(self, file_name: str) -> None:
        self.sound_manager.play_sound(file_name)
