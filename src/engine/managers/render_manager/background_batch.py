import pygame


class BackgroundBatch:
    def __init__(self, entity_width, entity_height, sprites, transforms):
        self.entity_width = entity_width
        self.entity_height = entity_height

        # Calculate the number of rows and columns
        min_x, max_x = float('inf'), float('-inf')
        min_y, max_y = float('inf'), float('-inf')

        for transform in transforms:
            pos = transform.get_position()
            if pos.x < min_x:
                min_x = pos.x
            if pos.x > max_x:
                max_x = pos.x
            if pos.y < min_y:
                min_y = pos.y
            if pos.y > max_y:
                max_y = pos.y

        self.cols = int((max_x - min_x) / entity_width) + 1
        self.rows = int((max_y - min_y) / entity_height) + 1

        self.batch_surface = pygame.Surface((self.cols * entity_width, self.rows * entity_height), pygame.SRCALPHA)
        self.batch_surface.fill((0, 0, 0, 0))  # Make the surface transparent

        # Offset to adjust positions relative to the origin
        self.offset_x = min_x
        self.offset_y = min_y

        # Add all tiles to the batch surface
        for sprite, transform in zip(sprites, transforms):
            self.add_entity(sprite, transform.get_position())

    def add_entity(self, sprite, position):
        x = int((position.x - self.offset_x))
        y = int((position.y - self.offset_y))
        self.batch_surface.blit(sprite, (x, -y + self.rows * self.entity_height - 1))

    def get_batch_surface(self):
        return self.batch_surface

    def get_width(self):
        return self.cols * self.entity_width

    def get_height(self):
        return self.rows * self.entity_height
