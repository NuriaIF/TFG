import pygame


class BackgroundBatch:
    def __init__(self, entity_width, entity_height, entities):
        self.entity_width = entity_width
        self.entity_height = entity_height

        # Calculate the number of rows and columns
        min_x = min(entity.get_transform().get_position().x for entity in entities)
        max_x = max(entity.get_transform().get_position().x for entity in entities)
        min_y = min(entity.get_transform().get_position().y for entity in entities)
        max_y = max(entity.get_transform().get_position().y for entity in entities)

        self.cols = int((max_x - min_x) / entity_width) + 1
        self.rows = int((max_y - min_y) / entity_height) + 1

        self.batch_surface = pygame.Surface((self.cols * entity_width, self.rows * entity_height), pygame.SRCALPHA)
        self.batch_surface.fill((0, 0, 0, 0))  # Make the surface transparent

        # Offset to adjust positions relative to the origin
        self.offset_x = min_x
        self.offset_y = min_y

        # Add all tiles to the batch surface
        for entity in entities:
            self.add_entity(entity.get_sprite(), entity.get_transform().get_position())

    def add_entity(self, sprite, position):
        x = int((position.x - self.offset_x))
        y = int((position.y - self.offset_y))
        self.batch_surface.blit(sprite, (x, y))

    def draw(self, surface, position):
        surface.blit(self.batch_surface, position)
