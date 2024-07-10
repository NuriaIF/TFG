"""
The command to swap to the previous map
"""
from src.game.game_state.menu.menu_actions.command import Command


class SwapMapPreviousCommand(Command):
    """
    Command to swap to the previous map
    """
    def __init__(self, menu_state):
        self.menu_state = menu_state

    def execute(self):
        """
        Execute the command
        :return:
        """
        print("Swap map previous button clicked")
        self.menu_state.current_map_index = (self.menu_state.current_map_index - 1) % len(self.menu_state.maps)

