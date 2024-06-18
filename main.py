import cProfile
import io
import os
import pstats
import time

import pygame

from engine.engine import Engine
from engine.fps_manager import FPSManager
from game.game import Game

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Initialize Pygame
    pygame.init()

    FPSManager(time_increment=1)
    game = Game()

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
            profiling_file = os.path.join(os.path.dirname(__file__), 'profiling_stats_v4.txt')
            with open(profiling_file, 'w') as f:
                ps = pstats.Stats(pr, stream=f).sort_stats('cumulative')
                ps.print_stats()
            pr.enable()  # Reiniciar el perfilado
            start_time = time.time()

    pygame.quit()
    exit()
