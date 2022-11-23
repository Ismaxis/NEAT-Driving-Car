import pygame
import os
import math

VEL = 7

CAR_SIZE = 100
STICK = pygame.image.load(os.path.join("images", "stick.png"))

class Car:
    SENSOR_ANGEL = 25
    IMG = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(os.path.join("images", "car.png")),
                                                            (CAR_SIZE, int(CAR_SIZE/2))), -90)
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.vel_x = 0
        self.vel_y = VEL
        self.image = self.IMG
        self.center = [self.image.get_rect().center[0] + self.x, self.image.get_rect().center[1] + self.y]
        self.distances = [0, 0]

    def rotate(self):
        tilt_rad = math.radians(self.tilt)
        sin = math.sin(tilt_rad)

        self.image = pygame.transform.rotate(self.IMG, self.tilt)


        self.vel_x = self.vel_y * sin
        self.x += -self.vel_x
        self.center[0] += -self.vel_x



    def draw(self, win):
        new_rect = self.image.get_rect(center=self.IMG.get_rect(topleft=(self.x, self.y)).center)
        win.blit(self.image, new_rect.topleft)

        # отрисовка линий зрения
        Car.drawline(win, new_rect.center, self.distances[0], self.tilt + self.SENSOR_ANGEL)
        Car.drawline(win, new_rect.center, self.distances[1], self.tilt - self.SENSOR_ANGEL)

    def get_mask(self):
        return pygame.mask.from_surface(self.IMG)

    def drawline(win, center, len, tilt):
        if len != math.inf:
            tilt_rad = math.radians(tilt)
            sin = math.sin(tilt_rad)
            cos = math.cos(tilt_rad)

            pygame.draw.line(win, (255, 255, 255), center, (center[0] - len * sin, center[1] - len * cos))
