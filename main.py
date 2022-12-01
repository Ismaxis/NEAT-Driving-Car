import math
import os
import numpy
import pygame
import neat

from BackGround import BG
from Car import Car
from RoadBlock import RoadBlock 
import Funcs

WIN_SIZE_X = 1000
WIN_SIZE_Y = 800
WIN = pygame.display.set_mode((WIN_SIZE_X, WIN_SIZE_Y))
pygame.display.set_caption("Race")
pygame.font.init()
STAT_FONT = pygame.font.SysFont("comics", 50)

ROTATE = 2


GEN = 0



def draw(win, cars, roads, bg, score, gen):

    bg.draw(win)

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

def main(genomes, config):
    global WIN, GEN
    GEN += 1

    nets = []
    ge = []
    cars = []
    
    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        cars.append(Car(WIN_SIZE_X / 2 + 25, 700))
        ge.append(genome)

    bg = BG()

    roads = [RoadBlock(450, 800)]
    for i in range(0, 6): 
        New_Block = RoadBlock(roads[i].x2, roads[i].y2)
        roads.append(New_Block)
    last_road = roads[len(roads) - 1]

    if last_road.x - 100 < 0:
        RoadBlock.COMPELLED_TURN = 1
    elif last_road.x + RoadBlock.GAP + 100 > WIN_SIZE_X:
        RoadBlock.COMPELLED_TURN = -1

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

        for i, car in enumerate(cars):
            if roads[0].collide(car):
                ge[i].fitness -= 1
                cars.pop(i)
                nets.pop(i)
                ge.pop(i)
                
            car.rotate()
            a1 = math.radians(car.tilt + Car.SENSOR_ANGEL)
            a2 = math.radians(car.tilt - Car.SENSOR_ANGEL)

            ray1 = pygame.Vector2(-math.sin(a1), -math.cos(a1)) 
            ray2 = pygame.Vector2(-math.sin(a2), -math.cos(a2))
            min_d1 = math.inf
            min_d2 = math.inf
            for road in roads:
                d1 = Funcs.distance_to_segment_by_ray(car.center, ray1, [[road.x, road.y], [road.x2, road.y2]])
                d2 = Funcs.distance_to_segment_by_ray(car.center, ray2, [[road.x + road.GAP, road.y],
                                                                   [road.x2 + road.GAP, road.y2]])
                if d1 < min_d1:
                    min_d1 = d1
                if d2 < min_d2:
                    min_d2 = d2

            car.distances = [min_d1, min_d2]
            if (i < len(cars)) :
                ge[i].fitness += 0.1
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

                if a_pressed and -RoadBlock.MAX_ROT <= car.tilt <= RoadBlock.MAX_ROT:
                    car.tilt += ROTATE
                elif d_pressed and -RoadBlock.MAX_ROT <= car.tilt <= RoadBlock.MAX_ROT:
                    car.tilt -= ROTATE

        rem = []
        add_road = False
        for road in roads:
            road.move()

            if road.y2 > WIN_SIZE_Y:
                rem.append(road)
                
            if not road.passed and len(cars) > 0 and road.y2 > cars[0].y:
                road.passed = True
                add_road = True

        if add_road:
            score += 1

            for g in ge:
                g.fitness += 5

            roads.append(RoadBlock(last_road.x2, last_road.y2)) 

            last_road = roads[len(roads) - 1]

        for r in rem:
            roads.remove(r)
        
        bg.move()
        draw(WIN, cars, roads, bg, score, GEN)
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
