from pygame import Vector2

from engine.engine import Engine
from engine.managers.input_manager.key import Key
from game.cars_manager import CarsManager
from game.NPC_manager import NPCManager
from game.game_mode import GameMode
from game.map.map_types import MapType
from game.map.tile_map import TileMap


# from interpretability_and_explainability.explainability_and_interpretability import ExplainabilityAndInterpretability


class Game(Engine):
    def __init__(self, chronometer):
        super().__init__()
        self.game_mode: GameMode = GameMode.MANUAL

        # self.play_music("GameMusic")

        self.tile_map: TileMap = TileMap(self, self.entity_manager)

        self.cars_manager = CarsManager(self.game_mode, self.tile_map, self.entity_manager, self.input_manager,
                                        self.renderer, self.debug_renderer, chronometer)
        self.npcs_manager = NPCManager(self.entity_manager, self.tile_map, self.debug_renderer)

        self._initialize()

        self.better_fitness_index = []

        self.explainability_and_interpretability = None
        self.chronometer = chronometer
        self.manual_camera = True

    def _initialize(self):
        self.cars_manager.initialize()
        self.npcs_manager.initialize()

    def _game_update(self, delta_time):
        self.cars_manager.update_cars(delta_time, self.npcs_manager.NPCs)
        self.npcs_manager.update_npc()
        self.move_camera()

    def _game_render(self):
        self._game_render_debug()
        for car in self.cars_manager.get_cars():
            if car.selected_as_parent:
                sprite_rect = self.entity_manager.get_sprite_rect(car.entity_ID)
                self.renderer.draw_rect(sprite_rect, (0, 0, 255), 3)
                car.selected_as_parent = False
        if len(self.cars_manager.get_ai_manager().get_agents()) > 0:
            sorted_list = sorted(self.cars_manager.get_ai_manager().get_agents(), key=lambda x: x.fitness_score, reverse=True)
            agent_with_best_fitness = sorted_list[0]
            self.debug_renderer.draw_rect_absolute(
                self.entity_manager.get_sprite_rect(agent_with_best_fitness.controlled_entity.entity_ID), (0, 255, 0),
                3)

    def move_camera(self):
        """
        The camera follows the car, if the car leaves a box centered on the camera, the camera moves to the car's position
        """
        if self.manual_camera:
            if self.input_manager.is_key_down(Key.K_UP):
                self.camera.move(Vector2(0, 300))
            if self.input_manager.is_key_down(Key.K_DOWN):
                self.camera.move(Vector2(0, -300))
            if self.input_manager.is_key_down(Key.K_LEFT):
                self.camera.move(Vector2(300, 0))
            if self.input_manager.is_key_down(Key.K_RIGHT):
                self.camera.move(Vector2(-300, 0))
        else:
            self._center_camera_on_car()

    def _center_camera_on_car(self):
        if len(self.cars_manager.get_cars()) == 1:
            car = self.cars_manager.get_cars()[0]
        else:
            agents = sorted(self.cars_manager.get_ai_manager().get_agents(), key=lambda x: x.fitness_score, reverse=True)
            car = agents[0].controlled_entity
        car_position = self.entity_manager.get_transform(car.entity_ID).get_position()
        camera_position = -self.camera.get_position()
        difference = camera_position - car_position
        if difference.length() > 1:
            self.camera.move(difference)

    def _game_render_debug(self):
        self._render_checkpoints()
        self.cars_manager.render_car_knowledge()
        self.npcs_manager.render_debug()

    def _render_checkpoints(self):
        for tile in self.tile_map.checkpoints:
            sprite_rect = self.entity_manager.get_sprite_rect(tile.entity_ID)
            transform = self.entity_manager.get_transform(tile.entity_ID)
            self.debug_renderer.draw_rect(sprite_rect.copy(), (255, 255, 0), 1)
            tile_position = transform.get_position()
            checkpoint_text_position: Vector2
            if tile.checkpoint_number < 10:
                checkpoint_text_position = Vector2(tile_position[0] + 4, tile_position[1])
            else:
                checkpoint_text_position = tile_position.copy()
            self.debug_renderer.draw_text(str(tile.checkpoint_number), checkpoint_text_position, (255, 255, 0))
        for tile in self.tile_map.checkpoint_lines:
            sprite_rect = self.entity_manager.get_sprite_rect(tile.entity_ID)
            self.debug_renderer.draw_rect(sprite_rect.copy(), (0, 255, 0), 1)
