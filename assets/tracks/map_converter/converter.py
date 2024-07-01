import numpy as np
from PIL import Image

TERRAIN_COLOR = (0, 255, 0)  # Green
SIDEWALK_COLOR = (195, 195, 195)  # Light gray
CROSSWALK_COLOR = (255, 255, 255)  # White
ROAD_COLOR = (0, 0, 0)  # Black
CAR_COLOR = (0, 0, 255)  # Blue
SEA_COLOR = (0, 162, 232)  # Light blue

color_to_char = {
        TERRAIN_COLOR: '\'',
        ROAD_COLOR: 'o',
        SIDEWALK_COLOR: '|',
        CROSSWALK_COLOR: 'i',
        CAR_COLOR: 'o',
        SEA_COLOR: 'T',
    }

def within_tolerance(color1, color2, tolerance=4):
    return all(abs(a - b) <= tolerance for a, b in zip(color1, color2))


def image_to_mlmap():
    image_name = input("Introduce el nombre del archivo de imagen (sin extensión): ")

    image = Image.open(image_name + ".png").convert('RGB')
    pixels = image.load()

    width, height = image.size

    ascii_str = ""

    for y in range(height):
        for x in range(width):
            color = pixels[x, y]
            tile_char = '*'  # Default if no match found

            for ref_color, char in color_to_char.items():
                if within_tolerance(color, ref_color):
                    tile_char = char
                    break

            if tile_char == '*':
                raise ValueError(f"Color {color} not recognized at ({x}, {y})")

            ascii_str += tile_char

        ascii_str += '\n'

    ascii_str = ascii_str[:-1]

    output_name = image_name + '.mlmap'

    with open('../' + output_name, 'w') as f:
        f.write(ascii_str)

    print(f"El contenido ASCII se ha guardado en {output_name}")


image_to_mlmap()
