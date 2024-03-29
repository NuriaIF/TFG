from pygame import Vector2

from engine.entities.entity import Entity

from game.map.tile_map import TileMap


class GameState:
    def __init__(self):
        self.agent_position: Vector2 = Vector2(0, 0)
        self.agent_forward: Vector2 = Vector2(0, 0)
        self.agent_velocity: float = 0
        self.agent_acceleration: float = 0
        # self.distances_to_sidewalk: list[int] = []
        # self.mapinfo: list[float] = []

    def update(self, agent: Entity) -> None:
        """
        Update the state of the game based on the action
        :param action:
        :return:
        """
        self.agent_position = agent.get_transform().get_position()

        # Input data
        self.agent_forward = agent.get_transform().get_forward()
        self.agent_velocity = agent.get_physics().get_velocity()
        self.agent_acceleration = agent.get_physics().acceleration
        # self.mapinfo = self.get_vision_tiles(game, tile_map, vision_range)
