import pygame
import os

import Car
bg_img = pygame.image.load(os.path.join("images", "bg.png"))

class BG:
    IMG = bg_img
    HEIGHT = bg_img.get_height()

    def __init__(self):
        self.y1 = 0
        self.y2 = -self.HEIGHT

    def move(self):
        self.y1 += Car.VEL
        self.y2 += Car.VEL
        if self.y1 > self.HEIGHT:
            self.y1 = self.y2 - self.HEIGHT

        if self.y2 > self.HEIGHT:
            self.y2 = self.y1 - self.HEIGHT

    def draw(self, win):
        win.blit(self.IMG, (0, self.y1))
        win.blit(self.IMG, (0, self.y2))

