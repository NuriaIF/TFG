"""
This module contains functions for geometry calculations.
"""
import numpy as np
from numpy import ndarray
from numba import njit, boolean, float64, uint32, uint64, int64


@njit(boolean(float64[:], float64[:, :]))
def point_in_polygon(point: ndarray, polygon: ndarray[ndarray]) -> bool:
    """
    Check if a point is inside a polygon.
    This uses the ray-casting algorithm for checking if a point is inside a polygon.
    :param point: Point to check if it is inside the polygon
    :param polygon: list of points that form the polygon to check if the point is inside
    :return: True if the point is inside the polygon, False otherwise.
    This is optimized using Numba.
    """
    intersection_x = 0
    x, y = point
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if p1y < y <= p2y or p2y < y <= p1y:
            if x <= max(p1x, p2x):
                if p1y != p2y:
                    intersection_x = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                if p1x == p2x or x <= intersection_x:
                    inside = not inside
        p1x, p1y = p2x, p2y

    return inside


@njit(float64[:](float64, float64, float64, float64, float64))
def rotate_point(x, y, center_x, center_y, angle):
    """
    Rotate a point around a center.
    This function rotates a point around a center by a given angle.
    Uses the rotation matrix to rotate the point.
    It is optimized using Numba.
    :param x: The x coordinate of the point
    :param y: The y coordinate of the point
    :param center_x: The x coordinate of the center
    :param center_y: The y coordinate of the center
    :param angle: The angle to rotate the point
    :return: The new coordinates of the point after rotation
    """
    angle_rad = np.radians(angle)
    cos_angle = np.cos(angle_rad)
    sin_angle = np.sin(angle_rad)

    # Translate point back to origin
    translated_x = x - center_x
    translated_y = y - center_y

    # Rotate point
    rotated_x = translated_x * cos_angle - translated_y * sin_angle
    rotated_y = translated_x * sin_angle + translated_y * cos_angle

    # Translate point back to its original location
    new_x = rotated_x + center_x
    new_y = rotated_y + center_y

    return np.array([new_x, new_y])


@njit(float64[:, :](float64, float64[:], float64[:], float64, uint32))
def calculate_polygon(angle: float, direction: ndarray, position: ndarray, tile_size: int,
                      radius: float = 6) -> ndarray:
    """
    Create the polygon for the field of view of the car in form of list of points (4 points).
    This also rotates the polygon around the center of the car by the angle.
    :param angle: The angle to rotate the polygon
    :param direction: The direction of the car
    :param position: The position of the car
    :param tile_size: The size of the tiles
    :param radius: The radius of the field of view
    :return: The rotated polygon of the field of view
    """
    center = np.zeros(2, dtype=np.float64)
    points = np.zeros((4, 2), dtype=np.float64)
    rotated_points = np.zeros((4, 2), dtype=np.float64)
    # Display the position 6 tiles in front of the car
    center[0] = position[0] + direction[0] * radius * tile_size
    center[1] = position[1] + direction[1] * radius * tile_size
    radius_pixels = radius * tile_size

    # Calculate the edges of the polygon
    points[0, 0] = center[0] + radius_pixels
    points[0, 1] = center[1] - radius_pixels
    points[1, 0] = center[0] + radius_pixels
    points[1, 1] = center[1] + radius_pixels
    points[2, 0] = center[0] - radius_pixels
    points[2, 1] = center[1] + radius_pixels
    points[3, 0] = center[0] - radius_pixels
    points[3, 1] = center[1] - radius_pixels

    # Rotate each point of the polygon around the center
    for i in range(4):
        rotated_points[i] = rotate_point(points[i, 0], points[i, 1], center[0], center[1], angle)

    return rotated_points
