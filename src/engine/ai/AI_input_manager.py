"""
This module contains the AIInputManager class
"""

import pygame

from src.engine.managers.input_manager.input_manager import InputManager


class AIInputManager(InputManager):
    """
    Input manager for AI agents. This class is responsible for converting the outputs of the neural network to commands.
    """
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

    def convert_outputs_to_commands(self, outputs: list[float]) -> None:
        """
        Convert the outputs of the neural network to commands, which are then used to update the key states.
        Keys corresponding with outputs > 0.5 are pressed.
        If there are two keys > 0.5, both are pressed.
        :param outputs: The outputs of the neural network
        """
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
        """
        Stop all keys from being pressed
        """
        for key in self.key_states:
            self.key_states[key] = False
