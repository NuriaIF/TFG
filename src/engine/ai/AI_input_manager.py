import pygame

from src.engine.managers.input_manager.input_manager import InputManager


class AIInputManager(InputManager):
    def __init__(self):
        # outputs to commands

        # Homologous attribute to what pygame.key.get_pressed() returns
        super().__init__()
        self.key_states = {
            pygame.K_w: False,
            pygame.K_s: False,
            pygame.K_d: False,
            pygame.K_a: False,
            pygame.K_LSHIFT: False,
            pygame.K_SPACE: False
        }
        self.keys = list(self.key_states.keys())

    def convert_outputs_to_commands(self, outputs: list[float]):
        # Keys corresponding with outputs > 0.5 are pressed
        # If there are two keys > 0.5, both are pressed
        # Convert list of outputs to list of keys
        # Update key states
        for i in range(len(outputs)):
            if outputs[i] > 0.5:
                self.key_states[self.keys[i]] = True
            else:
                self.key_states[self.keys[i]] = False

    def is_key_down(self, key) -> bool:
        return self._get_pressed()[key.value]

    def _get_pressed(self):
        return self.key_states

    def stop_keys(self):
        for key in self.key_states:
            self.key_states[key] = False
