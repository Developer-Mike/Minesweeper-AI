import random
import pygame
import assets


class Field:
    def __init__(self, pos, field_size):
        self.pos = pos
        self.abs_pos = (pos[0] * field_size, pos[1] * field_size)
        self.field_size = field_size
        self.field_rect = pygame.Rect(self.abs_pos[0], self.abs_pos[1], self.field_size, self.field_size)

        self.uncovered = False
        self.flagged = False
        self.bomb = random.randint(1, 10) == 1
        self.bombs_neighbour_count = 0

    def set_bomb_neighbours(self, fields):
        for neighbour in self.get_neighbours(fields):
            if neighbour.bomb:
                self.bombs_neighbour_count += 1

    def get_neighbours(self, fields):
        neighbours = []

        for y in range(self.pos[1] - 1, self.pos[1] + 2):
            for x in range(self.pos[0] - 1, self.pos[0] + 2):
                if len(fields) <= x or len(fields[0]) <= y or x < 0 or y < 0:
                    continue

                field = fields[x][y]
                if self == field:
                    continue

                neighbours.append(field)

        return neighbours

    def render(self, surface):
        if self.flagged:
            surface.blit(assets.FLAG, self.field_rect)
        elif not self.uncovered:
            surface.blit(assets.HIDDEN, self.field_rect)
        elif self.uncovered:
            if self.bomb:
                surface.blit(assets.MINE, self.field_rect)
            elif self.bombs_neighbour_count > 0:
                surface.blit(assets.NUMBERS[self.bombs_neighbour_count - 1], self.field_rect)
            else:
                surface.blit(assets.UNCOVERED, self.field_rect)

    def uncover(self, fields, from_player=True):
        if self.uncovered or self.flagged:
            return False

        self.uncovered = True
        if self.bomb and from_player:
            return True

        for neighbour in self.get_neighbours(fields):
            if not neighbour.uncovered and not neighbour.flagged and not neighbour.bomb and self.bombs_neighbour_count == 0:
                neighbour.uncover(fields, False)

        return False

    def toggle_flag(self):
        if self.uncovered:
            self.flagged = False
            return

        self.flagged = not self.flagged
