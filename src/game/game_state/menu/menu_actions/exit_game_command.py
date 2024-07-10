"""
This module contains the ExitGameCommand class
"""
from src.game.game_state.game_states_enum import StateEnum
from src.game.game_state.menu.menu_actions.command import Command


class ExitGameCommand(Command):
    """
    Command to exit the game
    """
    def __init__(self, game):
        self._game = game

    def execute(self):
        """
        Execute the command
        Will set the game state to exit
        :return:
        """
        print("Exit game button clicked")
        self._game.set_game_state(StateEnum.EXIT)
