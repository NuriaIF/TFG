from game.game_state.game_states_enum import StateEnum
from game.game_state.menu.menu_actions.command import Command
from game.game_state.races.watching_ai_state import WatchingAIState


class StartWatchAICommand(Command):
    def __init__(self, menu_state, game):
        self.menu_state = menu_state
        self.game = game

    def execute(self):
        print("Watch AI button clicked")
        self.game.set_map_name(self.menu_state.maps_names[self.menu_state.current_map_index])
        self.game.set_game_state(StateEnum.WATCHING_AI)
