import random

from pygame import Vector2

from engine.components.collider import Collider
from engine.managers.entity_manager.entity_manager import EntityManager
from engine.managers.render_manager.renderer import DebugRenderer
from game.entities.NPC import NPC
from game.entities.car import Car
from game.map.map_types import MapType
from game.map.tile_map import TileMap

seed = 1234

class NPCManager:
    def __init__(self, entity_manager: EntityManager, tile_map: TileMap, debug_renderer: DebugRenderer):
        self._entity_manager = entity_manager
        self._debug_renderer: DebugRenderer = debug_renderer
        self._tile_map: TileMap = tile_map
        self._NPCs: list[NPC] = []
        self._goal_range_person: int = 400
        self._road_probability_person: float = 0.1
        self._goal_range_bike: int = 1000
        self._road_probability_bike: float = 1
        # A margin of tiles in which the NPC can't spawn to avoid bugs
        self._map_margin_invalid: int = 8 + 4

    def get_NPCs(self) -> list[NPC]:
        return self._NPCs

    def is_npc_initial_pos_invalid(self, pos: Vector2) -> bool:
        """
        When spawning, npcs can't spawn on the road
        :param pos: position to check
        :return: True if the position is invalid, False otherwise
        """
        return self.is_npc_pos_invalid(pos) \
            or self._tile_map.get_tile_at_pos_vec(pos).tile_type == MapType.TRACK

    def is_npc_pos_invalid(self, pos: Vector2) -> bool:
        """
        Check if the NPC position is invalid
        This is used to calculate goals or spawn points
        It is invalid if the selected position doesn't fall within the map bounds
        or if it is too close to the edge of the map
        :param pos:
        :return:
        """
        tile_index = self._tile_map.get_tile_index_from_pos_vec(pos)
        tile_index_x = tile_index[0]
        tile_index_y = tile_index[1]
        return self._tile_map.get_tile_at_pos_vec(pos) is None \
            or self._tile_map.get_tile_at_pos_vec(pos).tile_type == MapType.SEA \
            or tile_index_x > self._tile_map.get_width_number() - self._map_margin_invalid \
            or tile_index_x < self._map_margin_invalid \
            or tile_index_y > self._tile_map.get_height_number() - self._map_margin_invalid \
            or tile_index_y < self._map_margin_invalid

    def npc_get_initial_random_pos(self) -> Vector2:
        while True:
            random_value_x: float = random.uniform(0, self._tile_map.width)
            random_value_y: float = random.uniform(0, self._tile_map.height)
            goal_position = Vector2(random_value_x, random_value_y)
            if not self.is_npc_initial_pos_invalid(goal_position):
                return goal_position

    def npc_get_random_pos(self, npc: NPC) -> Vector2:
        npc_position = npc.get_position()
        road_probability = npc.get_road_probability()
        goal_range = npc.get_goal_range()
        while True:
            random_value_x: float = random.uniform(-goal_range / 2, goal_range / 2)
            random_value_y: float = random.uniform(-goal_range / 2, goal_range / 2)
            goal_position = Vector2(npc_position.x + random_value_x,
                                    npc_position.y + random_value_y)
            if not self.is_npc_pos_invalid(goal_position):  # Check if the goal is valid
                # And if it is, check of it is on the road, if it is, return it with a certain probability
                # If the probability fails, keep looping until a valid goal is found
                if self._tile_map.get_tile_at_pos_vec(goal_position).tile_type == MapType.TRACK:
                    if random.random() < road_probability:
                        return goal_position
                    else:
                        continue
                return goal_position

    def render_debug(self):
        for npc in self._NPCs:
            self._debug_renderer.draw_circle(npc.get_goal().copy(), 5, (255, 0, 0), 3)
            self._debug_renderer.draw_line(npc.get_position().copy(), npc.get_goal().copy(), (255, 0, 0), 3)

    def update_npc(self):
        """
        NPCs should move randomly with random goals.
        They choose a random goal within a certain range and then move towards that goal.
        They check if the goal is valid (no collider, within map bounds).
        They enter the road with a certain low probability.
        """
        random.seed(seed)
        for npc in self._NPCs:
            if npc.is_on_goal() or self._entity_manager.get_collider(npc.entity_ID).is_colliding():
                random_goal: Vector2 = self.npc_get_random_pos(npc)
                npc.set_goal(random_goal)
            else:
                npc.move_towards_goal()
            # if self._game_mode is GameMode.AI_TRAINING:
            #     self._handle_npc_training(npc)

    def _handle_npc_training(self, npc: NPC):
        """
        Handle the behavior of an NPC while the program is in training mode
        When an NPC collides, it becomes static and collider-less
        """

        pass

    def create_npc_entities(self):
        number_of_people = 15
        number_of_bikes = 5
        if len(self._NPCs) == 0:
            for i in range(number_of_people):
                person = NPC(
                    self._entity_manager.create_entity("entities/person_head", has_collider=True, is_static=False),
                    self._entity_manager)

                self._NPCs.append(person)
                self._NPCs[i].set_goal_range(self._goal_range_person)
                self._NPCs[i].set_road_probability(self._road_probability_person)
                self._NPCs[i].set_npc_force(200)
            for j in range(number_of_people, number_of_people + number_of_bikes):
                bike = NPC(self._entity_manager.create_entity("entities/bicycle", has_collider=True, is_static=False),
                           self._entity_manager)
                self._NPCs.append(bike)
                self._NPCs[j].set_goal_range(self._goal_range_bike)
                self._NPCs[j].set_road_probability(self._road_probability_bike)

    def configure_npcs(self, cars: list[Car]):
        random.seed(seed)
        for npc in self._NPCs:
            npc.set_position(self.npc_get_initial_random_pos())
            npc.set_goal(npc.get_position())
            npc_collider: Collider = self._entity_manager.get_collider(npc.entity_ID)
            npc_physics = self._entity_manager.get_physics(npc.entity_ID)
            npc_physics.set_static(False)
            npc_collider.set_active(True)
            for other_npc in self._NPCs:
                other_npc_collider: Collider = self._entity_manager.get_collider(other_npc.entity_ID)
                if npc_collider is not other_npc_collider:
                    npc_collider.add_non_collideable_collider(other_npc_collider)
            # if self._game_mode is GameMode.AI_TRAINING:
            #     for car in cars:
            #         car_collider: Collider = self._entity_manager.get_collider(car.entity_ID)
            #         npc_collider.add_non_collideable_collider(car_collider)

    def initialize(self, cars: list[Car]):
        # self.create_npc_entities()
        self.configure_npcs(cars)
