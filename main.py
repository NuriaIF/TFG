import pygame

from src.engine.fps_manager import FPSManager
from src.game.game import Game
from src.game.AI.ai_info.chronometer import Chronometer


def main():
    # Initialize Pygame
    pygame.init()

    FPSManager(max_fps=30, time_increment=1)
    chrono = Chronometer()
    # chrono.start()
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
