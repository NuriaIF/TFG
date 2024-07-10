"""
This module contains the Window class, which is responsible for managing the window of the game.
"""

import pygame


class Window:
    """
    A class to manage the window of the game.
    """
    def __init__(self, title: str, width: int, height: int, fullscreen: bool = False):
        self.title = title
        self.width = width
        self.height = height
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)
        self.fullscreen = fullscreen

        self.WINDOW_BACKGROUND_COLOR = (51, 77, 77)

    def get_window(self) -> pygame.Surface:
        """
        Get the window of the game.
        :return: The window of the game
        """
        return self.window

    def get_width(self) -> int:
        """
        Get the width of the window.
        :return: The width of the window
        """
        return self.width

    def get_height(self) -> int:
        """
        Get the height of the window.
        :return: The height of the window
        """
        return self.height

    def get_title(self) -> str:
        """
        Get the title of the window.
        :return: The title of the window
        """
        return self.title

    def set_width(self, width) -> None:
        """
        Set the width of the window.
        :param width: The width of the window
        :return: None
        """
        self.width = width

    def set_height(self, height) -> None:
        """
        Set the height of the window.
        :param height: The height of the window
        :return: None
        """
        self.height = height

    def set_title(self, title):
        """
        Set the title of the window.
        :param title: The title of the window
        :return: None
        """
        self.title = title
        pygame.display.set_caption(self.title)

    @staticmethod
    def swap_buffers() -> None:
        """
        Swap the buffers of the window.
        Swapping buffers is the process of flipping the back buffer to the front buffer.
        :return: None
        """
        pygame.display.flip()

    def clear(self) -> None:
        """
        Clear the window, filling it with the background color.
        :return:
        """
        self.window.fill(self.WINDOW_BACKGROUND_COLOR)
