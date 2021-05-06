import math
import os
import random
import numpy
import pygame
import neat
pygame.font.init()


WIN_SIZE_X = 1000
WIN_SIZE_Y = 800
WIN = pygame.display.set_mode((WIN_SIZE_X, WIN_SIZE_Y))
pygame.display.set_caption("Race")
STAT_FONT = pygame.font.SysFont("comics", 50)

GAP = 200
VEL = 7
ROTATE = 2
MAX_ROT = 45
MAX_BIAS = 180
SENSOR_ANGEL = 25
CAR_ON_POS = False
COMPELLED_TURN = 0   # 1 - вправо, -1 - влево, если дорога вышла за экран

CAR_SIZE = 100
car_img = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(os.path.join("images", "car.png")),
                                                         (CAR_SIZE, int(CAR_SIZE/2))), -90)
road_img = pygame.transform.scale(pygame.image.load(os.path.join("images", "road.png")), (25, 300))
bg_img = pygame.image.load(os.path.join("images", "bg.png"))
stick_img = pygame.image.load(os.path.join("images", "stick.png"))

gen = 0


class Car:
    IMG = car_img
    STICK = stick_img

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
        global CAR_ON_POS

        tilt_rad = math.radians(self.tilt)
        sin = math.sin(tilt_rad)

        self.image = pygame.transform.rotate(self.IMG, self.tilt)


        self.vel_x = self.vel_y * sin
        self.x += -self.vel_x   # -смешение дороги
        self.center[0] += -self.vel_x

    def draw(self, win):
        new_rect = self.image.get_rect(center=self.IMG.get_rect(topleft=(self.x, self.y)).center)
        win.blit(self.image, new_rect.topleft)

        # отрисовка линий зрения
        drawline(new_rect.center, self.distances[0], self.tilt + SENSOR_ANGEL)
        drawline(new_rect.center, self.distances[1], self.tilt - SENSOR_ANGEL)

    def get_mask(self):
        return pygame.mask.from_surface(self.IMG)


def drawline(center, len, tilt):
    if len != math.inf:
        tilt_rad = math.radians(tilt)
        sin = math.sin(tilt_rad)
        cos = math.cos(tilt_rad)

        pygame.draw.line(WIN, (255, 255, 255), center, (center[0] - len * sin, center[1] - len * cos))


class RoadBlock:
    Len = 300
    Gap = GAP
    IMG = road_img

    def __init__(self, start_x, start_y):   # start_x координата конца левой палки по x
        global COMPELLED_TURN

        if COMPELLED_TURN == 1:
            COMPELLED_TURN = 0
            self.bias = random.randint(int(MAX_BIAS/2), MAX_BIAS)
        elif COMPELLED_TURN == -1:
            COMPELLED_TURN = 0
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
                 (self.x - self.bias / 2 + self.Gap + math.cos(math.radians(self.angle)) * 50, self.y)).center).center

        self.passed = False

    def get_rect_l(self):
        return self.image.get_rect(
            center=self.IMG.get_rect(topleft=(self.x - self.bias / 2, self.y)).center).topleft

    def get_rect_r(self):
        return self.image.get_rect(center=self.IMG.get_rect(topleft=(
            self.x - self.bias / 2 + self.Gap + math.cos(math.radians(self.angle)) * 50, self.y)).center).topleft

    def draw(self, win):
        rect_l = self.get_rect_l()
        rect_r = self.get_rect_r()

        pygame.draw.line(win, (255, 0, 0), (self.x, self.y), (self.x2, self.y2))
        pygame.draw.line(win, (0, 255, 0), (self.x + self.Gap, self.y), (self.x2 + self.Gap, self.y2))
        # win.blit(self.image, rect_l)
        # win.blit(self.image, rect_r)

    def move(self):
        self.y += VEL
        self.y2 += VEL

    def collide(self, car):
        Vec_1 = pygame.math.Vector2(self.x2 - self.x, self.y2 - self.y)
        Vec_2 = pygame.math.Vector2(car.center[0] - self.x, car.center[1] - self.y)

        Vec_3 = pygame.math.Vector2(self.x2 - self.x, self.y2 - self.y)
        Vec_4 = pygame.math.Vector2(car.center[0] - (self.x + self.Gap), car.center[1] - self.y)

        Cross = Vec_1.cross(Vec_2)
        Cross_2 = Vec_3.cross(Vec_4)

        if Cross < 0 or Cross_2 > 0:
            return True

        return False

    def get_distances(self, car):
        rect_l = self.get_rect_l()
        rect_r = self.get_rect_r()

        stick_mask = pygame.mask.from_surface(stick_img)
        curb_mask = pygame.mask.from_surface(self.image)

        left_offset = (int(rect_l[0] - car.x), rect_l[1] - car.y)
        right_offset = (int(rect_r[0] - car.x), rect_r[1] - car.y)

        left_point = stick_mask.overlap_area(curb_mask, left_offset)
        right_point = stick_mask.overlap_area(curb_mask, right_offset)

        return left_point, right_point


class BG:
    IMG = bg_img
    HEIGHT = bg_img.get_height()

    def __init__(self):
        self.y1 = 0
        self.y2 = -self.HEIGHT

    def move(self):
        self.y1 += VEL
        self.y2 += VEL
        if self.y1 > self.HEIGHT:
            self.y1 = self.y2 - self.HEIGHT

        if self.y2 > self.HEIGHT:
            self.y2 = self.y1 - self.HEIGHT

    def draw(self, win):
        win.blit(self.IMG, (0, self.y1))
        win.blit(self.IMG, (0, self.y2))


def distance_to_segment_by_ray(ray_start, ray_dir, line):
    Vec_1 = ray_dir
    Vec_2 = pygame.math.Vector2(line[0][0] - ray_start[0], line[0][1] - ray_start[1])
    Vec_3 = pygame.math.Vector2(line[1][0] - ray_start[0], line[1][1] - ray_start[1])

    Cross_1 = Vec_1.cross(Vec_2)
    Cross_2 = Vec_1.cross(Vec_3)

    if numpy.sign(Cross_1) != numpy.sign(Cross_2):
        color = (0, 255, 0)

        a = line[1][1] - line[0][1]
        b = line[0][0] - line[1][0]
        c = -line[0][0] * line[1][1] + line[0][1] * line[1][0]

        x0 = ray_start[0]
        y0 = ray_start[1]
        v = ray_dir[0]
        w = ray_dir[1]

        t = (-a*x0 - b*y0 - c) / (a*v +b*w)

        if t > 0:
            crossing_point = (ray_start[0] + v * t, ray_start[1] + w * t)
            distance = numpy.sqrt((ray_start[0] - crossing_point[0])**2 + (ray_start[1] - crossing_point[1])**2)
            return distance
        else:
            return math.inf
    else:
        return math.inf


def draw(win, cars, roads, bg, score, gen):
    win.fill((40, 160, 80))   # обновление экрана

    bg.draw(win)

    # pygame.draw.line(WIN, (255, 255, 255), (WIN_SIZE_X / 2, 0), (WIN_SIZE_X / 2, WIN_SIZE_Y))
    for car in cars:
        car.draw(win)

    for road in roads:
        road.draw(win)

    # score
    score_label = STAT_FONT.render("Score: " + str(score), True, (255, 255, 255))
    win.blit(score_label, (WIN_SIZE_X - score_label.get_width() - 15, 10))

    # generations
    score_label = STAT_FONT.render("Gens: " + str(gen - 1), True, (255, 255, 255))
    win.blit(score_label, (10, 10))

    # alive
    score_label = STAT_FONT.render("Alive: " + str(len(cars)), True, (255, 255, 255))
    win.blit(score_label, (10, 50))

    pygame.display.update()

"""
def get_distances(car, near_road, far_road):
    distances = []

    center = pygame.math.Vector2(car.center)
    near_l = pygame.math.Vector2(near_road.l_center)
    near_r = pygame.math.Vector2(near_road.r_center)
    far_l = pygame.math.Vector2(far_road.l_center)
    far_r = pygame.math.Vector2(far_road.r_center)

    distances.append(center.distance_to(near_l))
    distances.append(center.distance_to(near_r))
    distances.append(center.distance_to(far_l))
    distances.append(center.distance_to(far_r))

    return distances
"""

def main(genomes, config):
    global WIN, gen, CAR_ON_POS, COMPELLED_TURN
    gen += 1
    CAR_ON_POS = False

    nets = []
    ge = []
    cars = []  # [Car(WIN_SIZE_X / 2 - CAR_SIZE / 2, 700)]

    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        cars.append(Car(WIN_SIZE_X / 2 + 25, 700))
        ge.append(genome)

    bg = BG()

    roads = [RoadBlock(450, 800)]
    for i in range(0, 6):  # для биаса +- 100 размер 6, для +- 200 7
        New_Block = RoadBlock(roads[i].x2, roads[i].y2)
        roads.append(New_Block)
        # roads.append(RoadBlock(roads[i].x - roads[i].bias, roads[i].y - roads[i].Len))  #  * math.cos(math.radians(roads[i].angle))

    last_road = roads[len(roads) - 1]   # последняя созданная дорога, для того чтобы путь не уходил за экран

    if last_road.x - 100 < 0:
        COMPELLED_TURN = 1
    elif last_road.x + GAP + 100 > WIN_SIZE_X:
        COMPELLED_TURN = -1

    score = 0
    clock = pygame.time.Clock()
    a_pressed = False
    d_pressed = False
    main_run = True

    while main_run and len(cars) > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                main_run = False
                pygame.quit()
                quit()
                break

        for i, car in enumerate(cars):  # collide
            if roads[0].collide(car):
                ge[i].fitness -= 1
                cars.pop(i)
                nets.pop(i)
                ge.pop(i)

        for i, car in enumerate(cars):
            car.rotate()

            a1 = math.radians(car.tilt + SENSOR_ANGEL)
            a2 = math.radians(car.tilt - SENSOR_ANGEL)

            ray1 = pygame.Vector2(-math.sin(a1), -math.cos(a1))  # единичный вектор
            ray2 = pygame.Vector2(-math.sin(a2), -math.cos(a2))
            min_d1 = math.inf
            min_d2 = math.inf
            for road in roads:
                d1 = distance_to_segment_by_ray(car.center, ray1, [[road.x, road.y], [road.x2, road.y2]])
                d2 = distance_to_segment_by_ray(car.center, ray2, [[road.x + road.Gap, road.y],
                                                                   [road.x2 + road.Gap, road.y2]])
                if d1 < min_d1:
                    min_d1 = d1
                if d2 < min_d2:
                    min_d2 = d2

            car.distances = [min_d1, min_d2]

            ge[i].fitness += 0.1
            # distances = get_distances(car, roads[0], roads[1])

            output = nets[i].activate((car.distances[0], car.distances[1]))

            if output[0] > 0.5:
                ge[i].fitness += 0.1
                a_pressed = True
            elif output[0] < 0.5:
                a_pressed = False

            if output[1] > 0.5:
                ge[i].fitness += 0.1
                d_pressed = True
            elif output[1] < 0.5:
                d_pressed = False

            if a_pressed and -MAX_ROT <= car.tilt <= MAX_ROT:
                car.tilt += ROTATE
            elif d_pressed and -MAX_ROT <= car.tilt <= MAX_ROT:
                car.tilt -= ROTATE

        rem = []
        add_road = False
        for road in roads:
            road.move()

            if road.y2 > WIN_SIZE_Y:    # + road.Len*math.sin(math.radians(road.angle))
                rem.append(road)

            if not len(cars) > 0:
                break

            if not road.passed and road.y2 > cars[0].y:
                road.passed = True
                add_road = True

        if add_road:
            score += 1

            for g in ge:
                g.fitness += 5

            roads.append(RoadBlock(last_road.x2, last_road.y2))  # - last_road.Len * math.cos(math.radians(last_road.angle)

            last_road = roads[len(roads) - 1]

        for r in rem:
            roads.remove(r)
        """
        for i, car in enumerate(cars):
            if car.x - car.image.get_width() >= WIN_SIZE_X or car.x + car.image.get_width() <= 0:
                cars.pop(i)
                nets.pop(i)
                ge.pop(i)
        """
        bg.move()
        draw(WIN, cars, roads, bg, score, gen)
        clock.tick(30)


def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_file)

    population = neat.Population(config)

    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    winner = population.run(main, 50)

    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
