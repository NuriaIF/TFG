import pygame

from game.game_state.game_states_enum import StateEnum
from game.game_state.menu.menu_actions.command import Command


class ExitGameCommand(Command):
    def __init__(self, game):
        self._game = game
    def execute(self):
        print("Exit game button clicked")
        self._game.set_game_state(StateEnum.EXIT)
