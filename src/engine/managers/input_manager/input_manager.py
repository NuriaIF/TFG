"""
This module contains the input manager class.
"""
import pygame

from src.engine.managers.input_manager.key import Key, Mouse


class InputManager:
    """
    This is the input manager class. It is responsible for handling all the input events in the game.
    It is a wrapper around the pygame event handling system, and it provides methods to check for key presses.

    It has two parts:
     - The update that handles quit and mouse wheel events
     - The methods to check for key presses and mouse button presses
    """
    def __init__(self):
        self.scroll_up_detected = False
        self.scroll_down_detected = False

    def update(self) -> None:
        """
        Update the input manager.
        This method is responsible for handling the quit event and the mouse wheel event.
        :return: None
        """
        self.scroll_up_detected = False
        self.scroll_down_detected = False
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    self.scroll_up_detected = True
                elif event.y < 0:
                    self.scroll_down_detected = True

    def is_key_down(self, key: Key) -> bool:
        """
        Check if a key is pressed.
        :param key: The key to check
        :return: True if the key is pressed, False otherwise
        """
        return pygame.key.get_pressed()[key.value]

    def is_mouse_button_pressed(self, button: Mouse) -> bool:
        """
        Check if a mouse button is pressed.
        :param button: The mouse button to check
        :return: True if the mouse button is pressed, False otherwise
        """
        if button == Mouse.MOUSE_LEFT:
            return pygame.mouse.get_pressed()[0]
        elif button == Mouse.MOUSE_MIDDLE:
            return pygame.mouse.get_pressed()[1]
        elif button == Mouse.MOUSE_RIGHT:
            return pygame.mouse.get_pressed()[2]
        elif button == Mouse.MOUSE_SCROLL_UP:
            return self.scroll_up_detected
        elif button == Mouse.MOUSE_SCROLL_DOWN:
            return self.scroll_down_detected
        else:
            return False

    @staticmethod
    def get_mouse_position() -> tuple[int, int]:
        """
        Get the current position of the mouse.
        :return: The position of the mouse
        """
        return pygame.mouse.get_pos()
