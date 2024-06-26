import random

from pygame import Vector2

from engine.managers.entity_manager.entity_manager import EntityManager
from engine.managers.render_manager.renderer import DebugRenderer
from game.entities.NPC import NPC
from game.map.map_types import MapType
from game.map.tile_map import TileMap


class NPCManager:
    def __init__(self, entity_manager: EntityManager, tile_map: TileMap, debug_renderer: DebugRenderer):
        self.entity_manager = entity_manager
        self.debug_renderer: DebugRenderer = debug_renderer
        self.tile_map = tile_map
        self.NPCs: list[NPC] = []
        self.goal_range_person: int = 10
        self.goal_range_bike: int = 50
        self.road_probability: float = 0.1

    def is_npc_goal_invalid(self, goal_position: Vector2) -> bool:
        return self.tile_map.get_tile_at(goal_position) is None

    def npc_get_random_goal(self, npc_position: Vector2, goal_range: int) -> Vector2:
        while True:
            random_value: float = random.uniform(-goal_range/2, goal_range/2)
            goal_position = Vector2(npc_position.x + random_value,
                                    npc_position.y + random_value)
            if not self.is_npc_goal_invalid(goal_position):  # Check if the goal is valid
                # And if it is, check of it is on the road, if it is, return it with a certain probability
                # If the probability fails, keep looping until a valid goal is found
                if self.tile_map.get_tile_at(goal_position).tile_type == MapType.TRACK:
                    if random.random() < self.road_probability:
                        return goal_position
                    else:
                        continue
                return goal_position

    def render_debug(self):
        for npc in self.NPCs:
            self.debug_renderer.draw_circle(npc.get_goal(), 5, (255, 0, 0), 3)

    def update_npc(self):
        """
        NPCs should move randomly with random goals.
        They choose a random goal within a certain range and then move towards that goal.
        They check if the goal is valid (no collider, within map bounds).
        They enter the road with a certain low probability.
        Once on the road, the probability of setting the goal to a road is the same as other tiles.
        Once off the road, the probability of entering the road goes back to low.
        """
        goal_range: int = 100
        for npc in self.NPCs:
            if npc.is_on_goal():
                transform = self.entity_manager.get_transform(npc.entity_ID)
                npc_position = transform.get_position()
                random_goal: Vector2 = self.npc_get_random_goal(npc_position, goal_range)
                npc.set_goal(random_goal)
            else:
                npc.move_towards_goal()

    def initialize(self):
        self.NPCs: list[NPC] = []
        number_of_people = 5
        number_of_bikes = 0
        border_position = 8
        for i in range(number_of_people):
            person = NPC(self.entity_manager.create_entity("entities/person_head", has_collider=True, is_static=False),
                         self.entity_manager)
            self.NPCs.append(person)
            self.NPCs[i].set_position(Vector2(random.randint(a=border_position, b=border_position + 100) * 16 - 8,
                                              random.randint(a=border_position, b=border_position + 60) * 16 - 8))
        for j in range(number_of_people, number_of_people + number_of_bikes):
            bike = NPC(self.entity_manager.create_entity("entities/bicycle", has_collider=True, is_static=False),
                       self.entity_manager)
            self.NPCs.append(bike)
            self.NPCs[j].set_position(Vector2(random.randint(0, 100) * 16 - 8, random.randint(0, 60) * 16))
        for npc in self.NPCs:
            npc.set_goal(npc.get_position())
