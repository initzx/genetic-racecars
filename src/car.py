import time

import neat
import numpy as np
import pygame
from colorutils import Color


class Car(pygame.sprite.Sprite):
    WIDTH = 10
    HEIGHT = 15
    COLOR = 234

    FRICTION = 0.9
    ACCELERATION = 1.6
    MAX_SPEED = 5
    STEERING = 8

    LOOK = 400

    def __init__(self, simulation, genome, color=None, *groups):
        super().__init__(*groups)
        self.simulation = simulation
        self.conf = simulation.map_config.car_config
        self.genome = genome
        self.net = neat.nn.FeedForwardNetwork.create(genome, simulation.neat_config)
        self.alive = True
        genome.fitness = 0
        self.immunity = False
        self.alive_time = 0
        self.points = 0
        self.finishing_seq = [0, 1]
        self.finished = False
        self.previous_goal = None
        self.checkpoints = simulation.map_config.checkpoints # {1: game.starting_line, 0: game.finish_line}
        self.checkpoints_reached = set()

        self.specials = []

        self.color = Color(tuple(np.random.randint(256, size=3))) if not color else color
        self.image = self.original = pygame.Surface([Car.HEIGHT, Car.WIDTH])
        self.image.fill(self.color.rgb)
        self.image.set_colorkey((255, 0, 0))

        self.rect = self.image.get_rect(center=simulation.starting_pos)
        self.accel = pygame.Vector2(0, 0)
        self.speed = pygame.Vector2(0, 0)
        self.direction = self.original_dir = pygame.Vector2(1, 0)
        self.angle = 0

    @property
    def fitness(self):
        return self.genome.fitness

    def accelerate(self, f_or_b):
        self.accel += f_or_b*self.direction*self.conf['acceleration']

    def steer(self, r_or_l):
        self.angle += r_or_l*self.conf['steering'] #* np.random.rand()*2
        self.angle %= 360
        self.direction = self.original_dir.rotate(-self.angle)
        self.image = pygame.transform.rotate(self.original, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self, *args, **kwargs):
        self._AI_control()
        self.check_goals()

        if self.speed.length() != 0:
            normalized = self.speed.normalize()
            friction = -normalized*self.conf['friction'] * np.random.rand()*2
            self.accel += friction
            # if 'speed' in self.specials:
            #     self.speed *= 2
            # if 'slowness' in self.specials:
            #     self.speed *= 0.9

        self.speed += self.accel
        self.accel *= 0
        self.speed = self.speed.normalize() * max(-self.conf['max_speed'],
                                                  min(self.speed.length(), self.conf['max_speed']))
        self.rect.move_ip(self.speed)

        try:
            if self.simulation.map.get_at(self.rect.center)[0] == 255:
                self.die()
        except IndexError:
            self.die()

    def check_goals(self):
        finish = self.checkpoints['finish']
        start = self.checkpoints['start']
        checkpoints = self.checkpoints['checkpoints']
        car_line = [self.rect.center, self.rect.center + self.direction * 7]

        if intersect(car_line, finish['coords']):
            if not self.finished:
                self.genome.fitness += finish['points']
            self.reached_goals = []
            self.finished = True

        if intersect(car_line, start['coords']):
            if self.finished and not self.immunity:
                self.genome.fitness += start['points']
                self.immunity = True
            elif not self.finished:
                self.die()

        if self.immunity and not intersect(car_line, start['coords']):
            self.immunity = False
            self.finished = False

        goals_to_go = self.checkpoints_reached ^ set(checkpoints)
        for goal in goals_to_go:
            if intersect(car_line, checkpoints[goal]['coords']):
                self.checkpoints_reached.add(goal)
                self.genome.fitness += checkpoints[goal]['points']

    def _AI_control(self):
        f, l, r = self.simulation.sensor_check_on_track(self.rect.center, self.direction, self.conf['look']).values()
        control = self.net.activate([self.speed.length(), f, l, r])

        steering = -1
        accelerate = -1
        if control[0] < control[-1]:
            steering = 1

        if control[2] < control[3]:
            accelerate = 1

        self.accelerate(accelerate)
        self.steer(steering)

    def die(self):
        self.kill()
        self.alive = False
        self.alive_time = time.time() - self.simulation.start


def ccw(A,B,C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])


def intersect(A, B):
    return ccw(A[0], B[0], B[1]) != ccw(A[1], B[0], B[1]) and ccw(A[0], A[1], B[0]) != ccw(A[0], A[1], B[1])