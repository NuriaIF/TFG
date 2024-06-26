import pygame

from engine.fps_manager import FPSManager
from game.game import Game
from game.game_state.chronometer import Chronometer


def main():
    # Initialize Pygame
    pygame.init()

    FPSManager(time_increment=1)
    chrono = Chronometer()
    chrono.start()
    game = Game(chrono)

    # Clock for controlling frame rate and calculating delta time
    running = True

    while running:
        # Calculate delta time
        FPSManager.start_frame()

        game.update(FPSManager.get_delta_time())
        game.render()

    pygame.quit()
    exit()


if __name__ == '__main__':
    main()