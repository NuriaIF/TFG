"""
This module contains the ExplainabilityManager class.
"""
import pygame
from pygame import Vector2


class ExplainabilityManager:
    """
    This class is responsible for rendering the explainability of the neural network.
    """
    def __init__(self, renderer):
        """
        Initialize the ExplainabilityManager
        :param renderer: The renderer to render the explainability
        """
        self._renderer = renderer
        self._color_map = {
            1.0: (0, 0, 0),
            -0.5: (155, 155, 155),
            -1.0: (0, 255, 0),
            -2.0: (0, 0, 255),
        }

        self._actions = ['Forward', 'Backward', 'Right', 'Left', 'Accelerate', 'Brake']

    def render_explainability(self, inputs, outputs):
        """
        Render the explainability of the neural network
        :param inputs: inputs of the neural network
        :param outputs: outputs of the neural network
        """
        self._render_neural_network(inputs, outputs)

    def _render_neural_network(self, inputs, outputs):
        rect = pygame.rect.Rect(10, 20, 305, 240)
        self._renderer.draw_rect_absolute(rect, (0, 162, 232), 0)
        self._renderer.draw_rect_absolute(rect, (0, 0, 0), 3)
        self._renderer.draw_text_absolute("INPUTS", Vector2(85, 30), (0, 0, 0), bold=True)
        self._renderer.draw_text_absolute("OUTPUTS", Vector2(225, 30), (0, 0, 0), bold=True)
        self._render_input_neurons(inputs)
        self._render_output_neurons(outputs)

    def _render_input_neurons(self, inputs):
        self._render_field_of_view(inputs[3:])
        # render other inputs
        self._renderer.draw_circle_absolute(Vector2(5 + 12 * 11, 60), 5, (0, 0, 0), 5)
        self._renderer.draw_text_absolute(str(round(inputs[0], 2)), Vector2(5 + 12 * 11 + 10, 60 - 10), (0, 0, 0))
        self._renderer.draw_text_absolute("speed", Vector2(95, 60 - 10), (0, 0, 0))
        self._renderer.draw_circle_absolute(Vector2(5 + 12 * 11, 60 + 12), 5, (0, 0, 0), 5)
        self._renderer.draw_text_absolute(str(round(inputs[1], 2)), Vector2(5 + 12 * 11 + 10, 60 + 12 - 10), (0, 0, 0))
        self._renderer.draw_text_absolute("x to next checkpoint", Vector2(20, 60 + 12 - 10), (0, 0, 0))
        self._renderer.draw_circle_absolute(Vector2(5 + 12 * 11, 60 + 12 * 2), 5, (0, 0, 0), 5)
        self._renderer.draw_text_absolute(str(round(inputs[2], 2)), Vector2(5 + 12 * 11 + 10, 60 + 12 * 2 - 10),
                                          (0, 0, 0))
        self._renderer.draw_text_absolute("y to next checkpoint", Vector2(20, 60 + 12 * 2 - 10), (0, 0, 0))

    def _render_output_neurons(self, outputs):
        position_x = 235
        position_y = 90
        distance = 20
        border_color = (0, 0, 0)
        for i in range(len(outputs)):
            if outputs[i] > 0.5:
                color = (255, 255, 255)
                text_color = (255, 255, 255)
            else:
                color = (0, 0, 0)
                text_color = (0, 0, 0)
            self._renderer.draw_circle_absolute(Vector2(position_x, position_y + i * distance), 5, color, 5)
            self._renderer.draw_circle_absolute(Vector2(position_x, position_y + i * distance), 5, border_color, 2)
            self._renderer.draw_text_absolute(str(self._actions[i]),
                                              Vector2(position_x + 10, position_y + i * distance - 10),
                                              text_color)

    def _render_field_of_view(self, field_of_view: list[float]):
        width = 12
        position_x = 35
        position_y = 110
        for i in range(width):
            for j in range(width):
                index = i * width + j
                value = field_of_view[index]
                color = self._color_map[value]
                self._renderer.draw_circle_absolute(Vector2(position_x + j * 12, position_y + i * 12), 5, color, 5)
