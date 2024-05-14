import pygame as pygame

class Intersection:
    def __init__(self, intersects: bool, intersection_area: float):
        self.intersects = intersects
        self.intersection_area = intersection_area

    def get_intersects(self) -> bool:
        return self.intersects

    def get_intersection_area(self) -> float:
        return self.intersection_area

class Collider:
    def __init__(self, rect: pygame.Rect, is_training: bool):
        if rect is None:
            raise ValueError("Rect cannot be None")
        if not isinstance(rect, pygame.Rect):
            raise ValueError("Rect must be an instance of pygame.Rect")
        self.rect = rect
        self.is_in_training = is_training

    def get_rect(self) -> pygame.Rect:
        return self.rect

    def update_rect(self, rect: pygame.Rect) -> None:
        if rect is None:
            raise ValueError("Rect cannot be None")
        if not isinstance(rect, pygame.Rect):
            raise ValueError("Rect must be an instance of pygame.Rect")
        self.rect = rect

    def intersects(self, other_collider: 'Collider') -> Intersection:
        """
        Returns a tuple with a boolean value and a float value. The boolean value is True if the collider intersects.
        The float is the area of the intersection. If the boolean value is False, the float value is 0.
        """
        if not isinstance(other_collider, Collider):
            raise ValueError("other_collider must be an instance of Collider")

        # Check for intersection
        intersects = self.rect.colliderect(other_collider.get_rect())
        if intersects:
            # Calculate intersection rectangle
            intersection_rect = self.rect.clip(other_collider.get_rect())
            # Calculate area of intersection
            intersection_area = intersection_rect.width * intersection_rect.height
            return Intersection(True, intersection_area)
        else:
            return Intersection(False, 0.0)
