"""
StartTrainAICommand class
"""
from src.game.game_state.game_states_enum import StateEnum
from src.game.game_state.menu.menu_actions.command import Command


class StartTrainAICommand(Command):
    """
    Command to start the game in training mode
    """
    def __init__(self, menu_state, game):
        self.menu_state = menu_state
        self.game = game

    def execute(self):
        """
        Execute the command
        Will set the game state to training
        :return:
        """
        print("Train new AI button clicked")
        self.game.set_map_name(self.menu_state.maps_names[self.menu_state.current_map_index])
        self.game.set_game_state(StateEnum.TRAINING)
