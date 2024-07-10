"""
This script converts an image to a map file.
"""
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


def within_tolerance(color1: tuple[int, int, int], color2: tuple[int, int, int], tolerance: int = 4):
    """
    Check if two colors are within a certain tolerance.
    :param color1:
    :param color2:
    :param tolerance: the maximum difference between the RGB values
    :return: true if the colors are within the tolerance, false otherwise
    """
    return all(abs(a - b) <= tolerance for a, b in zip(color1, color2))


def image_to_map():
    """
    Convert an image to a map file.
    This function will prompt the user for the name of the image file (without extension) and will save the
    ASCII content to a file with the same name and a .mlmap extension.
    :return: None
    """
    image_name = input("Introduce the name of the image file (without extension): ")

    # Load the image and convert to RGB mode
    try:
        image = Image.open("../tracks_images/" + image_name + ".png").convert('RGB')
    except FileNotFoundError:
        print(f"Image {image_name} not found")
        return

    pixels = image.load()
    width, height = image.size

    ascii_str = ""

    for y in range(height):
        for x in range(width):
            if pixels is None:
                raise ValueError(f"Image {image_name} not found")
            # noinspection PyUnresolvedReferences
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

    print(f"ASCII content saved to {output_name}")


image_to_map()
