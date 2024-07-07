from pygame import Vector2

from src.engine.components.transform import Transform
from src.engine.engine import Engine
from src.engine.managers.entity_manager.entity_manager import EntityManager
from src.engine.managers.input_manager.input_manager import InputManager
from src.engine.managers.input_manager.key import Key
from src.engine.managers.render_manager.renderer import DebugRenderer
from src.game.ai.ai_info.chronometer import Chronometer

from src.game.cars_manager import CarsManager
from src.game.entities.car import Car
from src.game.entities.tile import Tile
from src.game.game_state.exit_state import ExitState

from src.game.game_state.game_states_enum import StateEnum
from src.game.game_state.igame_state import IGameState
from src.game.game_state.menu.menu_state import MenuState
from src.game.game_state.races.player_vs_ai_state import PlayerVsAIState
from src.game.game_state.races.playing_state import PlayingState
from src.game.game_state.races.training_state import TrainingState

from src.game.game_state.races.watching_ai_state import WatchingAIState
from src.game.map.tile_map import TileMap


class Game(Engine):

    def __init__(self, chronometer):
        super().__init__()

        # self.play_music("GameMusic")

        self._chronometer = chronometer
        self._input_manager = InputManager()
        self._tile_map = None
        self._current_map_name = None
        self._cars_manager = None
        self._manual_camera = False

        self.exit_key_pressed = False

        self._explainability_manager = None

        self._game_states: dict[StateEnum, IGameState] = {
            StateEnum.MENU: MenuState(self, StateEnum.MENU),
            StateEnum.PLAYING: PlayingState(self, StateEnum.PLAYING),
            StateEnum.PLAYER_VS_AI: PlayerVsAIState(self, StateEnum.PLAYER_VS_AI),
            StateEnum.TRAINING: TrainingState(self, StateEnum.TRAINING),
            StateEnum.WATCHING_AI: WatchingAIState(self, StateEnum.WATCHING_AI),
            StateEnum.EXIT: ExitState(self, StateEnum.EXIT)
        }

        self._current_state: StateEnum = StateEnum.MENU
        # From the menu state, the game will start
        self._game_states[StateEnum.MENU].link_to_state(StateEnum.PLAYING)
        self._game_states[StateEnum.MENU].link_to_state(StateEnum.PLAYER_VS_AI)
        self._game_states[StateEnum.MENU].link_to_state(StateEnum.TRAINING)
        self._game_states[StateEnum.MENU].link_to_state(StateEnum.WATCHING_AI)
        self._game_states[StateEnum.MENU].link_to_state(StateEnum.EXIT)

        self._game_states[StateEnum.PLAYING].link_to_state(StateEnum.MENU)
        self._game_states[StateEnum.PLAYER_VS_AI].link_to_state(StateEnum.MENU)
        self._game_states[StateEnum.TRAINING].link_to_state(StateEnum.MENU)
        self._game_states[StateEnum.WATCHING_AI].link_to_state(StateEnum.MENU)

    def get_input_manager(self):
        return self._input_manager

    def get_current_state(self) -> IGameState:
        return self._game_states[self._current_state]

    def set_game_state(self, state: StateEnum) -> None:
        assert self._game_states[self._current_state].can_change_to_state(state), \
            "State " + self._current_state.__str__() + " cannot be changed to state " + state.__str__()
        self._game_states[self._current_state].destruct()
        self._current_state = state
        self.initialize()

    def _game_initialize(self):
        self.get_current_state().initialize()

    def start_game(self):
        self._tile_map: TileMap = TileMap(self._entity_manager)
        self._tile_map.load_map(self._current_map_name)
        self._cars_manager: CarsManager = CarsManager(self._tile_map, self._entity_manager,
                                                      self.renderer, self.debug_renderer,
                                                      self._tile_map.distance_between_checkpoints,
                                                      self._chronometer)

        self.get_tile_map().generate_tiles()

    def _game_reset(self):
        self._cars_manager.initialize()

    def _game_update(self, delta_time):
        self.get_current_state().update(delta_time)

    def _game_render(self):
        self.get_current_state().render()

    def move_camera(self):
        """
        The camera follows the car, if the car leaves a box centered on the camera, the camera moves to the car's position
        """
        if self._manual_camera:
            if self._input_manager.is_key_down(Key.K_UP):
                self.camera.move(Vector2(0, 300))
            if self._input_manager.is_key_down(Key.K_DOWN):
                self.camera.move(Vector2(0, -300))
            if self._input_manager.is_key_down(Key.K_LEFT):
                self.camera.move(Vector2(-300, 0))
            if self._input_manager.is_key_down(Key.K_RIGHT):
                self.camera.move(Vector2(300, 0))
        else:
            self._center_camera_on_car()

    def _center_camera_on_car(self):
        if 0 < len(self._cars_manager.get_cars()) <= 2:
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
        self.get_current_state().render_debug()

    def render_checkpoints(self):
        for tile in self._tile_map.checkpoints:
            sprite_rect = self._entity_manager.get_sprite_rect(tile.entity_ID)
            transform = self._entity_manager.get_transform(tile.entity_ID)
            self.debug_renderer.draw_rect(sprite_rect.copy(), (255, 255, 0), 1)
            tile_position = transform.get_position()
            checkpoint_text_position: Vector2
            if tile.checkpoint_number < 10:
                checkpoint_text_position = Vector2(tile_position[0] + 4, tile_position[1])
            else:
                checkpoint_text_position = tile_position
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

    def get_tile_map(self) -> TileMap:
        return self._tile_map

    def get_cars_manager(self) -> CarsManager:
        return self._cars_manager

    def get_entity_manager(self) -> EntityManager:
        return self._entity_manager

    def get_debug_renderer(self) -> DebugRenderer:
        return self.debug_renderer

    def get_chronometer(self) -> Chronometer:
        return self._chronometer

    def set_map_name(self, map_name):
        self._current_map_name = map_name

    def game_clear(self):
        print("Clearing game")
        self._entity_manager.clear()
        self._tile_map.clear()
        self._cars_manager.clear()
        self._chronometer.reset()
        self.renderer.render_clear()
        self.background_batch_created = False
        self.collider_manager.clear()

    def set_explainability_manager(self, explainability_manager):
        self._explainability_manager = explainability_manager

    def get_explainability_manager(self):
        return self._explainability_manager
