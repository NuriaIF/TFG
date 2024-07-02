
class GameStateMachine:
    def __init__(self):
        self.states = {}
        self.current_state = None

    def add_state(self, state):
        self.states[state.name] = state

    def set_state(self, state_name):
        if self.current_state:
            self.current_state.exit()
        self.current_state = self.states[state_name]
        self.current_state.enter()

    def update(self, dt):
        if self.current_state:
            self.current_state.update(dt)