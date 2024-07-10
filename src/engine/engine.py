"""
This module contains the Engine class.
"""
from pygame import Vector2, Rect

from src.engine.camera import Camera
from src.engine.engine_fonts import EngineFonts
from src.engine.managers.collider_manager.collider_manager import ColliderManager

from src.engine.managers.entity_manager.entity_manager import EntityManager
from src.engine.managers.fps_manager import FPSManager
from src.engine.managers.input_manager.input_manager import InputManager
from src.engine.managers.input_manager.key import Key
from src.engine.managers.physics_manager.physics_manager import PhysicsManager
from src.engine.managers.render_manager.renderer import Renderer, DebugRenderer
from src.engine.managers.sound_manager.sound_manager import SoundManager

from src.engine.managers.window_manager.window import Window
from src.game.camera_coordinates import CameraCoords


class Engine:
    """
    This is the heart of the engine and the game.
    It contains all the managers and coordinates them to work together.
    Also separates the debug rendering from the game rendering.
    """
    def __init__(self):
        self.window = Window("Game", 1200, 800, fullscreen=True)
        self._input_manager = InputManager()
        self.renderer = Renderer(self.window)
        self.debug_renderer = DebugRenderer(self.window)
        self.physics_manager = PhysicsManager()
        self.sound_manager = SoundManager()
        self.engine_fonts = EngineFonts()
        self._entity_manager = EntityManager()
        self.collider_manager = ColliderManager(self._entity_manager, self.debug_renderer)
        self.camera = Camera()
        self.background_batch_created = False
        self._is_second_update = False
        self._running = True

    def is_running(self) -> bool:
        """
        Check if the engine is running.
        Must be called in the main loop.
        :return:
        """
        return self._running

    def exit_running(self) -> None:
        """
        Exits the engine running state.
        Must be called to exit the main loop.
        :return: None
        """
        self._running = False

    def initialize(self) -> None:
        """
        Initialize the engine and the game.
        :return: None
        """
        self._game_initialize()
        for entity in self._entity_manager.entities:
            if self._entity_manager.get_collider(entity).is_active():
                self.collider_manager.send_data(entity)

    def reset(self) -> None:
        """
        Reset the engine and the game.
        """
        print("RESET")
        for entity in self._entity_manager.entities:
            if not self._entity_manager.get_physics(entity).is_static():
                self._entity_manager.reset_entity(entity)
        self._game_reset()

    def handle_engine_inputs(self) -> None:
        """
        Handle the inputs of the engine. Enable and disable debug mode.
        :return: None
        """
        if self._input_manager.is_key_down(Key.K_O):
            self.debug_renderer.enable_debug_mode()
        if self._input_manager.is_key_down(Key.K_P):
            self.debug_renderer.disable_debug_mode()

    def update(self, delta_time: float) -> None:
        """
        Main update loop of the engine.
        This method iterates over the entities and calls the update methods of the managers on their component.
        Also updates the rect of the collider and the batch sprites.
        :param delta_time:
        :return:
        """
        self._input_manager.update()
        self.handle_engine_inputs()
        self._game_update(delta_time)
        self.camera.update(delta_time)
        CameraCoords.update_window_size(Vector2(self.window.get_width(), self.window.get_height()))
        batch_sprites = []
        batch_transforms = []

        for entity in self._entity_manager.entities:
            # Getting the next frame collider before updating the physics
            # This way a collider never enters another, blocking the entity
            transform = self._entity_manager.get_transform(entity)
            physics = self._entity_manager.get_physics(entity)
            sprite = self._entity_manager.get_sprite(entity)
            collider = self._entity_manager.get_collider(entity)
            if not physics.is_static():
                self.physics_manager.update(entity, physics, transform, self._entity_manager, delta_time)

            sprite_rect: Rect = self._entity_manager.get_sprite_rect(entity)
            collider.update_rect(sprite_rect)
            is_batched = self._entity_manager.is_batched(entity)
            layer = self._entity_manager.get_layer(entity)
            self.renderer.update(sprite, transform, is_batched, layer)

            if is_batched:
                batch_transforms.append(transform)
                batch_sprites.append(sprite)

        if len(self._entity_manager.entities) > 0 and not self.background_batch_created:
            self.renderer.create_background_batch(batch_sprites, batch_transforms)
            self.background_batch_created = True

        # This only work the second update onwards
        # Because needs the rects from the sprites updated and for them to be updated
        # They need to be rendered first
        if self._is_second_update:
            self.collider_manager.update()
        self._is_second_update = True

    def _draw_fps(self) -> None:
        """
        Draw the FPS on the screen for debugging purposes.
        :return: None
        """
        self.debug_renderer.draw_text_absolute(f"FPS: {round(FPSManager.get_average_fps(), 2)}", Vector2(0, 0))

    def draw_camera_position(self) -> None:
        """
        Draw the camera position on the screen for debugging purposes.
        :return: None
        """
        self.debug_renderer.draw_text_absolute(f"Camera Position: {self.camera.get_position()}", Vector2(0, 20))

    def _draw_entity_debug_information(self) -> None:
        """
        Draws all the debug information of the entities.
        :return: None
        """
        for entity in self._entity_manager.entities:
            collider = self._entity_manager.get_collider(entity)
            transform = self._entity_manager.get_transform(entity)
            self.debug_renderer.draw_collider(collider)
            self.debug_renderer.draw_transform(transform)
            self.debug_renderer.draw_forward_vector(transform)

    def render(self) -> None:
        """
        Main render loop of the engine.
        This will render the game and the debug information if debug mode is enabled.
        :return:
        """
        self.window.clear()
        self.renderer.render()
        self._game_render()

        if self.debug_renderer.debug_mode:
            self._game_render_debug()
            self._draw_entity_debug_information()
            self.draw_camera_position()
            self.collider_manager.debug_render()
            self._draw_fps()

        self.window.swap_buffers()

    def _game_initialize(self):
        """
        Initialize the game.
        This must be implemented in the game class.
        :return:
        """
        pass

    def _game_reset(self):
        """
        Reset the game.
        This must be implemented in the game class.
        :return:
        """
        pass

    def _game_update(self, delta_time: float):
        """
        Update the game.
        This must be implemented in the game class.
        :param delta_time:
        :return:
        """
        pass

    def _game_render(self):
        """
        Render for specific game rendering that is not supposed by the engine.
        This must be implemented in the game class.
        :return:
        """
        pass

    def _game_render_debug(self):
        """
        Render for specific game debugging rendering that is not supposed by the engine.
        This must be implemented in the game class.
        :return:
        """
        pass

    def play_music(self, file_name: str) -> None:
        """
        Play the music of the game.
        :param file_name: The name of the music file
        :return: None
        """
        self.sound_manager.play_music(file_name)

    def play_sound(self, file_name: str) -> None:
        """
        Play a sound effect.
        :param file_name: The name of the sound file
        :return: None
        """
        self.sound_manager.play_sound(file_name)
