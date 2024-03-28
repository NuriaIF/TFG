from enum import Enum

import pygame


class Key(Enum):
    # WASD
    K_W = pygame.K_w
    K_A = pygame.K_a
    K_S = pygame.K_s
    K_D = pygame.K_d

    K_O = pygame.K_o
    K_P = pygame.K_p

    K_UP = pygame.K_UP
    K_DOWN = pygame.K_DOWN
    K_LEFT = pygame.K_LEFT
    K_RIGHT = pygame.K_RIGHT

    # Space
    K_SPACE = pygame.K_SPACE
    K_SHIFT = pygame.K_LSHIFT

    # Escape
    K_ESCAPE = pygame.K_ESCAPE


class Mouse(Enum):
    # Mouse buttons
    MOUSE_LEFT = 1
    MOUSE_MIDDLE = 2
    MOUSE_RIGHT = 3
    MOUSE_SCROLL_UP = 4
    MOUSE_SCROLL_DOWN = 5
