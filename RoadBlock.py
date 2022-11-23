import pygame
import os
import random
import math

import Car

MAX_BIAS = 180

class RoadBlock:
    MAX_ROT = 45
    GAP = 200
    COMPELLED_TURN = 0
    Len = 300
    IMG =  pygame.transform.scale(pygame.image.load(os.path.join("images", "road.png")), (25, 300))
    

    def __init__(self, start_x, start_y):
        
        if self.COMPELLED_TURN == 1:
            self.COMPELLED_TURN = 0
            self.bias = random.randint(int(MAX_BIAS/2), MAX_BIAS)
        elif self.COMPELLED_TURN == -1:
            self.COMPELLED_TURN = 0
            self.bias = random.randint(-MAX_BIAS, int(-MAX_BIAS/2))
        elif random.randint(0, 1) == 0:
            self.bias = random.randint(int(MAX_BIAS/2), MAX_BIAS)
        else:
            self.bias = random.randint(-MAX_BIAS, int(-MAX_BIAS/2))

        self.angle = math.degrees(math.asin(self.bias/self.Len))
        self.image = pygame.transform.rotozoom(self.IMG, self.angle, 1)

        self.x = start_x
        self.y = start_y

        self.x2 = self.x - self.bias
        self.y2 = self.y - self.Len

        self.l_center = self.image.get_rect(
            center=self.IMG.get_rect(topleft=(self.x - self.bias / 2, self.y)).center).center
        self.r_center = self.image.get_rect(center=self.IMG.get_rect(topleft=
                 (self.x - self.bias / 2 + self.GAP + math.cos(math.radians(self.angle)) * 50, self.y)).center).center

        self.passed = False

    def get_rect_l(self):
        return self.image.get_rect(
            center=self.IMG.get_rect(topleft=(self.x - self.bias / 2, self.y)).center).topleft

    def get_rect_r(self):
        return self.image.get_rect(center=self.IMG.get_rect(topleft=(
            self.x - self.bias / 2 + self.GAP + math.cos(math.radians(self.angle)) * 50, self.y)).center).topleft

    def draw(self, win):
        rect_l = self.get_rect_l()
        rect_r = self.get_rect_r()

        pygame.draw.line(win, (255, 0, 0), (self.x, self.y), (self.x2, self.y2))
        pygame.draw.line(win, (0, 255, 0), (self.x + self.GAP, self.y), (self.x2 + self.GAP, self.y2))

    def move(self):
        self.y += Car.VEL
        self.y2 += Car.VEL

    def collide(self, car):
        Vec_1 = pygame.math.Vector2(self.x2 - self.x, self.y2 - self.y)
        Vec_2 = pygame.math.Vector2(car.center[0] - self.x, car.center[1] - self.y)

        Vec_3 = pygame.math.Vector2(self.x2 - self.x, self.y2 - self.y)
        Vec_4 = pygame.math.Vector2(car.center[0] - (self.x + self.GAP), car.center[1] - self.y)

        Cross = Vec_1.cross(Vec_2)
        Cross_2 = Vec_3.cross(Vec_4)

        if Cross < 0 or Cross_2 > 0:
            return True

        return False

    def get_distances(self, car):
        rect_l = self.get_rect_l()
        rect_r = self.get_rect_r()

        stick_mask = pygame.mask.from_surface(Car.STICK)
        curb_mask = pygame.mask.from_surface(self.image)

        left_offset = (int(rect_l[0] - car.x), rect_l[1] - car.y)
        right_offset = (int(rect_r[0] - car.x), rect_r[1] - car.y)

        left_point = stick_mask.overlap_area(curb_mask, left_offset)
        right_point = stick_mask.overlap_area(curb_mask, right_offset)

        return left_point, right_point
