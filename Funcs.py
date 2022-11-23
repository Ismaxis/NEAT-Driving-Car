import math
import numpy
import pygame

def distance_to_segment_by_ray(ray_start, ray_dir, line):
    Vec_1 = ray_dir
    Vec_2 = pygame.math.Vector2(line[0][0] - ray_start[0], line[0][1] - ray_start[1])
    Vec_3 = pygame.math.Vector2(line[1][0] - ray_start[0], line[1][1] - ray_start[1])

    Cross_1 = Vec_1.cross(Vec_2)
    Cross_2 = Vec_1.cross(Vec_3)

    if numpy.sign(Cross_1) != numpy.sign(Cross_2):
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
