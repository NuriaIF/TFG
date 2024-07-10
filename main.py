"""
Main file of the game
"""

import pygame

from src.engine.managers.fps_manager import FPSManager
from src.game.ai.ai_info.chronometer import Chronometer
from src.game.game import Game


def main():
    """
    Main function of the game
    """
    # Initialize Pygame
    pygame.init()

    FPSManager(max_fps=30, time_increment=1)
    chrono = Chronometer()

    game = Game(chrono)
    game.initialize()

    while game.is_running():
        # Calculate delta time
        FPSManager.start_frame()

        game.update(FPSManager.get_delta_time())
        game.render()

    pygame.quit()
    exit()


if __name__ == '__main__':
    main()
