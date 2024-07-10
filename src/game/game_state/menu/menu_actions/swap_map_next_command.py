"""
The command to swap to the next map
"""

from src.game.game_state.menu.menu_actions.command import Command


class SwapMapNextCommand(Command):
    """
    Command to swap to the next map
    """
    def __init__(self, menu_state):
        self.menu_state = menu_state

    def execute(self):
        """
        Execute the command
        Will swap to the next map
        :return:
        """
        print("Swap map next button clicked")
        self.menu_state.current_map_index = (self.menu_state.current_map_index + 1) % len(self.menu_state.maps)
