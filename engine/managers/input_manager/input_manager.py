import pygame

from engine.managers.input_manager.key import Key, Mouse


class InputManager:
    def __init__(self):
        self.scroll_up_detected = False
        self.scroll_down_detected = False

    def update(self):
        self.scroll_up_detected = False
        self.scroll_down_detected = False
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    self.scroll_up_detected = True
                elif event.y < 0:
                    self.scroll_down_detected = True

    def is_key_down(self, key: Key) -> bool:
        return pygame.key.get_pressed()[key.value]

    def is_mouse_button_pressed(self, button: Mouse) -> bool:
        if button == Mouse.MOUSE_LEFT:
            return pygame.mouse.get_pressed(3)[0]
        elif button == Mouse.MOUSE_MIDDLE:
            return pygame.mouse.get_pressed(3)[1]
        elif button == Mouse.MOUSE_RIGHT:
            return pygame.mouse.get_pressed(3)[2]
        elif button == Mouse.MOUSE_SCROLL_UP:
            return self.scroll_up_detected
        elif button == Mouse.MOUSE_SCROLL_DOWN:
            return self.scroll_down_detected
        else:
            return False

    def get_mouse_position(self) -> tuple[int, int]:
        return pygame.mouse.get_pos()
