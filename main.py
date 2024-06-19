import pygame

from engine.fps_manager import FPSManager
from game.game import Game

def main():
    # Initialize Pygame
    pygame.init()

    FPSManager(time_increment=1)
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


if __name__ == '__main__':
    main()