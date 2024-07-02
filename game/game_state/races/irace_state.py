from overrides import overrides
from abc import abstractmethod

from engine.managers.input_manager.key import Key
from game.game_state.game_states_enum import StateEnum
from game.game_state.igame_state import IGameState


class IRaceState(IGameState):
    def __init__(self, game, state_enum):
        super().__init__(game, state_enum)

    def initialize_race(self, number_of_cars: int):
        self._game.start_game()
        self._game.get_cars_manager().set_number_of_cars(number_of_cars)
        self._create_cars()
        self._game.get_cars_manager().initialize()

    def _handle_go_to_menu_input(self):
        if self._game.get_input_manager().is_key_down(Key.K_ESCAPE):
            self._game.set_game_state(StateEnum.MENU)

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def update(self, delta_time):
        self._game.move_camera()
        self._handle_go_to_menu_input()
        pass

    @abstractmethod
    def render(self):
        pass

    @abstractmethod
    def render_debug(self):
        pass

    @overrides
    def destruct(self):
        self._game.game_clear()

    @abstractmethod
    def _create_cars(self):
        pass
