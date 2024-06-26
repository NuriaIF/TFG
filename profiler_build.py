import cProfile
import os
import pstats
import time
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
    pr = cProfile.Profile()
    pr.enable()
    start_time = time.time()
    profile_duration = 10

    while running:
        # Calculate delta time
        FPSManager.start_frame()

        game.render()
        game.update(FPSManager.get_delta_time())

        # Detener el perfilado después de cierto tiempo
        if time.time() - start_time > profile_duration:
            print("deteniendo el perfilado")
            pr.disable()
            profiling_file = os.path.join(os.path.dirname(__file__), 'profilers/training_mode/profiling_test_v01.txt')
            with open(profiling_file, 'w') as f:
                ps = pstats.Stats(pr, stream=f).sort_stats('cumulative')
                ps.print_stats()
            pr.enable()  # Reiniciar el perfilado
            start_time = time.time()

    pygame.quit()
    exit()


if __name__ == '__main__':
    main()