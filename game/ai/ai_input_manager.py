import pygame

from engine.managers.input_manager.input_manager import InputManager


class AIInputManager(InputManager):
    def __init__(self):
        # outputs to commands

        # Atributo homólogo a lo que devuelve pygame.key.get_pressed()
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
        # Simulando que la AI "presiona" la tecla de arriba
        # ai_input_manager.simulated_key_states[pygame.K_UP] = True
        # Tengo que hacer un mapeo de los outputs a las teclas
        # Si tengo outputs [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        # La tecla que más presiono son las > 0.1
        # Si tengo dos mayores a 0.1, me quedo con ambas
        # Convert list of outputs to list of keys
        # Update key states
        for i in range(len(outputs)):
            if outputs[i] > 0.1:
                self.key_states[self.keys[i]] = True

    # herencia de InputManager
    def is_key_down(self, key) -> bool:
        return self._get_pressed()[key.value]

    def _get_pressed(self):
        return self.key_states
