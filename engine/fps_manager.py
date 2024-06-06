import pygame


class FPSManager:
    _instance = None
    fps_history: list[float]  # List to store FPS history
    average_fps: float  # Stores the calculated average FPS
    max_fps: int  # Maximum FPS limit
    clock: pygame.time.Clock  # Pygame clock object
    time_increment: float  # Time increment

    def __new__(cls, max_fps: int = 60, time_increment: float = 1.0):
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
        return cls._instance.average_fps

    @classmethod
    def start_frame(cls):
        """Call this at the start of each frame to cap the frame rate"""
        cls._instance.calculate_avg_fps(cls._instance.get_delta_time())
        cls._instance.clock.tick(cls._instance.max_fps)

    @classmethod
    def get_delta_time(cls) -> float:
        """Returns the time in seconds since the last frame"""
        return (cls._instance.clock.get_time() / 1000.0) * cls._instance.time_increment
