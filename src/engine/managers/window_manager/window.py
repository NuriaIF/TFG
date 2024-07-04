import pygame


class Window:
    def __init__(self, title: str, width: int, height: int, fullscreen: bool = False):
        self.title = title
        self.width = width
        self.height = height
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)
        self.fullscreen = fullscreen

        self.WINDOW_BACKGROUND_COLOR = (51, 77, 77)

    def get_window(self):
        return self.window

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_title(self):
        return self.title

    def set_width(self, width):
        self.width = width

    def set_height(self, height):
        self.height = height

    def set_title(self, title):
        self.title = title
        pygame.display.set_caption(self.title)

    def swap_buffers(self):
        pygame.display.flip()

    def clear(self):
        self.window.fill(self.WINDOW_BACKGROUND_COLOR)
