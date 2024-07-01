from pygame import Vector2

from engine.engine import Engine
from engine.managers.input_manager.key import Key
from game.NPC_manager import NPCManager
from game.cars_manager import CarsManager
from game.game_mode import GameMode
from game.map.tile_map import TileMap


# from interpretability_and_explainability.explainability_and_interpretability import ExplainabilityAndInterpretability


class Game(Engine):
    def __init__(self, chronometer):
        super().__init__()
        self._game_mode: GameMode = GameMode.AI_TRAINING

        # self.play_music("GameMusic")

        self._tile_map: TileMap = TileMap(self._entity_manager)

        self._cars_manager = CarsManager(self._game_mode, self._tile_map, self._entity_manager, self.input_manager,
                                         self.renderer, self.debug_renderer,
                                         self._tile_map.distance_between_checkpoints, chronometer)
        # self._npcs_manager = NPCManager(self._entity_manager, self._tile_map, self.debug_renderer, self._game_mode)

        self.better_fitness_index = []

        self._explainability_and_interpretability = None
        self._chronometer = chronometer
        self._manual_camera = False

        self.menu = False

    def _game_initialize(self):
        self._tile_map.generate_tiles()
        self._cars_manager.initialize()
        # self._npcs_manager.initialize(self._cars_manager.get_cars())

    def _game_reset(self):
        self._cars_manager.initialize()
        # self._npcs_manager.initialize(self._cars_manager.get_cars())

    def _game_update(self, delta_time):
        if self._cars_manager.get_ai_manager().has_generation_ended():
            self.reset()
            self._cars_manager.get_ai_manager().next_generation()
        self._cars_manager.update_cars(delta_time)
        # self._npcs_manager.update_npc()
        self.move_camera()

    def _game_render(self):
        if self._game_mode == GameMode.AI_TRAINING:
            self.debug_renderer.draw_text_absolute(
                "Generation: " + str(self._cars_manager.get_ai_manager().genetic_algorithm.current_generation),
                Vector2(100, 100),
                (255, 255, 255))

    def move_camera(self):
        """
        The camera follows the car, if the car leaves a box centered on the camera, the camera moves to the car's position
        """
        if self._manual_camera:
            if self.input_manager.is_key_down(Key.K_UP):
                self.camera.move(Vector2(0, 300))
            if self.input_manager.is_key_down(Key.K_DOWN):
                self.camera.move(Vector2(0, -300))
            if self.input_manager.is_key_down(Key.K_LEFT):
                self.camera.move(Vector2(-300, 0))
            if self.input_manager.is_key_down(Key.K_RIGHT):
                self.camera.move(Vector2(300, 0))
        else:
            self._center_camera_on_car()

    def _center_camera_on_car(self):
        if len(self._cars_manager.get_cars()) == 1:
            car = self._cars_manager.get_cars()[0]
        else:
            agents = sorted(self._cars_manager.get_ai_manager().get_agents(), key=lambda x: x.fitness_score,
                            reverse=True)
            car = agents[0].controlled_entity
        car_position = self._entity_manager.get_transform(car.entity_ID).get_position()
        camera_position = self.camera.get_position()
        difference = car_position - camera_position
        if difference.length() > 1:
            self.camera.move(difference)

    def _game_render_debug(self):
        self._render_checkpoints()
        self._cars_manager.render_car_knowledge()
        # self._render_tile_rects()
        # self._render_tile_positions()

        self._cars_manager.render_debug()
        # self._npcs_manager.render_debug()


    def _render_checkpoints(self):
        for tile in self._tile_map.checkpoints:
            sprite_rect = self._entity_manager.get_sprite_rect(tile.entity_ID)
            transform = self._entity_manager.get_transform(tile.entity_ID)
            self.debug_renderer.draw_rect(sprite_rect.copy(), (255, 255, 0), 1)
            tile_position = transform.get_position()
            checkpoint_text_position: Vector2
            if tile.checkpoint_number < 10:
                checkpoint_text_position = Vector2(tile_position[0] + 4, tile_position[1])
            else:
                checkpoint_text_position = tile_position.copy()
            self.debug_renderer.draw_text(str(tile.checkpoint_number), checkpoint_text_position, (255, 255, 0))
        for tile in self._tile_map.checkpoint_lines:
            sprite_rect = self._entity_manager.get_sprite_rect(tile.entity_ID)
            self.debug_renderer.draw_rect(sprite_rect.copy(), (0, 255, 0), 1)

    def _render_tile_rects(self):
        for tile in self._tile_map.tiles:
            sprite_rect = self._entity_manager.get_sprite_rect(tile.entity_ID)
            self.debug_renderer.draw_rect(sprite_rect.copy(), (10, 200, 30), 1)

    def _render_tile_positions(self):
        for tile in self._tile_map.tiles:
            transform = self._entity_manager.get_transform(tile.entity_ID).copy()
            self.debug_renderer.draw_circle(transform.get_position(), 2, (255, 0, 0), 1)
