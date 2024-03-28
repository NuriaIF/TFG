import time

import pygame

from engine.engine import Engine
from engine.fps_manager import FPSManager
from game.game import Game

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Initialize Pygame
    pygame.init()

    FPSManager()
    game = Game()

    # Clock for controlling frame rate and calculating delta time
    running = True
    while running:
        # Calculate delta time
        FPSManager.start_frame()

        game.render()
        game.update(FPSManager.get_delta_time())

    pygame.quit()
    exit()
