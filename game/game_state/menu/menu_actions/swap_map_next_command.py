from game.game_state.menu.menu_actions.command import Command


class SwapMapNextCommand(Command):
    def __init__(self, menu_state):
        self.menu_state = menu_state

    def execute(self):
        print("Swap map next button clicked")
        self.menu_state.current_map_index = (self.menu_state.current_map_index + 1) % len(self.menu_state.maps)
