"""
This module contains the FPSManager class.
"""
import pygame


class FPSManager:
    """
    This class handles the FPS of the game.
    Will ensure that the game runs at a consistent frame rate, using the Pygame clock object.
    Also, will provide with a delta time to make the physics frame rate independent.
    This class is a singleton, so it will only be instantiated once and must be accessed through the instance method.
    """
    _instance = None
    fps_history: list[float]  # List to store FPS history
    average_fps: float  # Stores the calculated average FPS
    max_fps: int  # Maximum FPS limit
    clock: pygame.time.Clock  # Pygame clock object
    time_increment: float  # Time increment

    def __new__(cls, max_fps: int = 30, time_increment: float = 1.0):
        if cls._instance is None:
            cls._instance = super(FPSManager, cls).__new__(cls)
            # Initialize without type hints
            cls._instance.fps_history = []
            cls._instance.average_fps = 0
            cls._instance.max_fps = max_fps
            cls._instance.clock = pygame.time.Clock()
            cls._instance.time_increment = time_increment
        return cls._instance

    @classmethod
    def calculate_avg_fps(cls, delta_time: float) -> float:
        """
        Calculate the average FPS of the game.
        :param delta_time: The time passed since the last frame
        :return: The average FPS
        """
        if delta_time == 0:
            return 0
        fps = 1.0 / delta_time
        cls._instance.fps_history.append(fps)
        if len(cls._instance.fps_history) > 60:  # Keep the last 60 readings
            cls._instance.fps_history.pop(0)
        cls._instance.average_fps = sum(cls._instance.fps_history) / len(cls._instance.fps_history)
        return cls._instance.average_fps

    @classmethod
    def get_average_fps(cls) -> float:
        """
        Get the average FPS of the game.
        :return: The average FPS
        """
        return cls._instance.average_fps

    @classmethod
    def start_frame(cls):
        """
        This must be called at the start of each frame to cap the frame rate.
        It starts the clock and calculates the average FPS.
        :return:
        """
        cls._instance.calculate_avg_fps(cls._instance.get_delta_time())
        cls._instance.clock.tick(cls._instance.max_fps)

    @classmethod
    def get_delta_time(cls) -> float:
        """
        This returns the delta time
        The delta time is the time passed since the last frame in seconds.
        :return:
        """
        return (cls._instance.clock.get_time() / 1000.0) * cls._instance.time_increment
