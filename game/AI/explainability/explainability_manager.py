from pygame import Vector2

from game.entities.tile import Tile
from game.map.map_types import MapType


class ExplainabilityManager:
    def __init__(self, renderer):
        self._renderer = renderer
        self._color_map = {
            1.0: (0, 0, 0),
            -0.5: (155, 155, 155),
            -1.0: (0, 255, 0),
            -2.0: (0, 0, 255),
        }

    def render_explainability(self, inputs, outputs):
        self.render_neural_network(inputs, outputs)

    def render_neural_network(self, inputs, outputs):
        self._render_input_neurons(inputs)

    def _render_input_neurons(self, inputs):
        self._render_field_of_view(inputs[3:])
        # render other inputs

    def _render_output_neurons(self, outputs):
        # render outputs
        pass

    def _render_field_of_view(self, field_of_view: list[float]):
        TRACK = 1.0
        CROSSWALK = 1.0
        SIDEWALK = -0.5
        GRASS = -1.0
        FOREST = -1.0
        SEA = -2.0
        width = 12
        for i in range(width):
            for j in range(width):
                value = field_of_view[i * width + j]
                color = self._color_map[value]
                self._renderer.draw_circle_absolute(Vector2(i * 10, j * 10), 5, color, 5)

        # for tile, vector in zip(field_of_view, positions):
        #     pos = Vector2(center[0] + vector[0], center[1] - vector[1])
        #     if tile.tile_type == MapType.TRACK:
        #         self._renderer.draw_circle_absolute(pos, 5, (0, 0, 0), 5)
        #     elif tile.tile_type == MapType.GRASS:
        #         self._renderer.draw_circle_absolute(pos, 5, (0, 255, 0), 5)
        #     elif tile.tile_type == MapType.SIDEWALK:
        #         self._renderer.draw_circle_absolute(pos, 5, (155, 155, 155), 5)
        #     elif tile.tile_type == MapType.SEA:
        #         self._renderer.draw_circle_absolute(pos, 5, (0, 0, 255), 5)


