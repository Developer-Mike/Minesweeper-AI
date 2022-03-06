import random
import pygame
from field import Field
import assets


def flatten(array):
    flat_array = []
    for sub_array in array:
        flat_array.extend(sub_array)
    return flat_array


class Game:
    def __init__(self, surface, field_count, field_size):
        self.won = None
        self.time = 0
        self.surface = surface
        self.field_count = field_count
        self.field_size = field_size
        self.info_render_y = field_size * field_count[1]

        self.fields = [[Field((x, y), field_size) for y in range(field_count[1])] for x in range(field_count[0])]
        self.flag_count = 0
        self.bomb_count = 0
        for field in flatten(self.fields):
            field.set_bomb_neighbours(self.fields)
            if field.bomb:
                self.bomb_count += 1
        self.uncover_first()

    def uncover_first(self):
        first_uncovered = False
        while not first_uncovered:
            random_field = self.fields[random.randint(0, self.field_count[0] - 1)][random.randint(0, self.field_count[1] - 1)]
            if not random_field.bomb and random_field.bombs_neighbour_count == 0:
                random_field.uncover(self.fields)
                first_uncovered = True

    def make_move(self):
        made_move = False

        for y in range(self.field_count[1]):
            for x in range(self.field_count[0]):
                field = self.fields[x][y]

                if not field.uncovered:
                    continue

                neighbours = field.get_neighbours(self.fields)

                if field.bombs_neighbour_count == sum(not neighbour.uncovered for neighbour in neighbours):
                    for neighbour in neighbours:
                        if not neighbour.uncovered and not neighbour.flagged:
                            self.place_flag(neighbour)
                            made_move = True

                if field.bombs_neighbour_count == sum(neighbour.flagged for neighbour in neighbours):
                    for neighbour in neighbours:
                        if not neighbour.uncovered and not neighbour.flagged:
                            self.uncover_field(neighbour)
                            made_move = True

                if made_move:
                    return

        print("Impossible")
        for field in flatten(self.fields):
            if field.bomb:
                field.uncover(self.fields)
        self.won = False

    def uncover_field(self, field):
        game_over = field.uncover(self.fields)
        if game_over:
            for field in flatten(self.fields):
                if field.bomb:
                    field.uncover(self.fields)

            self.won = False

    def place_flag(self, field):
        field.toggle_flag()
        self.flag_count += 1 if field.flagged else -1

    def render(self):
        self._render_fields()
        self._render_info()

    def _render_fields(self):
        all_fields_uncovered = True
        for field in flatten(self.fields):
            field.render(self.surface)

            if not field.uncovered and not field.bomb:
                all_fields_uncovered = False

        if all_fields_uncovered:
            self.won = True

    def _render_info(self):
        # Erase previous stuff
        pygame.draw.rect(self.surface, (0, 0, 0), pygame.Rect(0, self.info_render_y, self.surface.get_height(), self.surface.get_width()))

        # Render flag count
        self.surface.blit(assets.FLAG, pygame.Rect(0, self.info_render_y, self.surface.get_height(), self.field_size))

        font = pygame.font.Font(None, self.field_size)
        text = font.render(str(self.bomb_count - self.flag_count), True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.left = self.field_size + 10
        text_rect.centery = self.info_render_y + self.field_size / 2
        self.surface.blit(text, text_rect)

        # Render time
        self.surface.blit(assets.FLAG, pygame.Rect(0, self.info_render_y, self.surface.get_height(), self.field_size))

        font = pygame.font.Font(None, self.field_size)
        text = font.render(str(int(self.time)), True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.right = self.surface.get_width() - 10
        text_rect.centery = self.info_render_y + self.field_size / 2
        self.surface.blit(text, text_rect)
