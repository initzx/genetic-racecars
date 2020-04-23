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
    ACCELERATION = 1.2
    MAX_SPEED = 5
    STEERING = 5

    LOOK = 100

    def __init__(self, simulation, genome, color=None, *groups):
        super().__init__(*groups)
        self.simulation = simulation
        self.genome = genome
        genome.fitness = 0
        self.net = neat.nn.FeedForwardNetwork.create(genome, simulation.neat_config)
        self.alive = True

        self.immunity = False
        self.alive_time = 0
        self.points = 0
        self.finishing_seq = [0, 1]
        self.finished = False
        self.previous_goal = None
        self.goals = simulation.goals # {1: game.starting_line, 0: game.finish_line}
        self.checkpoints_reached = set()

        self.specials = []

        self.color = Color(tuple(np.random.randint(256, size=3))) if not color else color
        self.image = self.original = pygame.Surface([Car.HEIGHT, Car.WIDTH])
        self.image.fill(self.color.rgb)
        self.image.set_colorkey((255, 0, 0))

        self.rect = self.image.get_rect(center=(421, 115))
        self.accel = pygame.Vector2(0, 0)
        self.speed = pygame.Vector2(0, 0)
        self.direction = self.original_dir = pygame.Vector2(1, 0)
        self.angle = 0

    @property
    def fitness(self):
        return self.genome.fitness

    def accelerate(self, f_or_b):
        self.accel += f_or_b*self.direction*Car.ACCELERATION

    def steer(self, r_or_l):
        self.angle += r_or_l*Car.STEERING * np.random.rand()*2
        self.angle %= 360
        self.direction = self.original_dir.rotate(-self.angle)
        self.image = pygame.transform.rotate(self.original, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self, *args, **kwargs):
        self._AI_control()

        if self.speed.length() != 0:
            friction = -self.speed.normalize()*Car.FRICTION #* np.random.rand()*2
            self.accel += friction
            self.speed = self.speed.normalize()*max(-Car.MAX_SPEED, min(self.speed.length(), Car.MAX_SPEED))
            if 'speed' in self.specials:
                self.speed *= 2
            if 'slowness' in self.specials:
                self.speed *= 0.9

        self.speed += self.accel
        self.accel *= 0
        self.rect.move_ip(self.speed)

        try:
            if self.simulation.map.get_at(self.rect.center)[0] == 255:
                self.die()
        except IndexError:
            self.die()

        self.check_goals_1()

    def check_goals_1(self):
        finish = self.goals['finish']
        start = self.goals['start']
        checkpoints = self.goals['checkpoints']
        car_line = [self.rect.center, self.rect.center + self.direction * 20]

        if intersect(car_line, finish['coords']):
            if not self.finished:
                self.genome.fitness += finish['points']
            self.reached_goals = []
            self.finished = True

        if intersect(car_line, start['coords']):
            if self.finished:
                self.genome.fitness += start['points']
                self.immunity = True
            elif not self.finished:
                self.die()

        if self.immunity and not intersect(car_line, start['coords']):
            self.immunity = False

        goals_to_go = self.checkpoints_reached ^ set(checkpoints.keys())
        for goal in goals_to_go:
            if intersect(car_line, checkpoints[goal]['coords']):
                self.checkpoints_reached.add(goal)
                self.genome.fitness += checkpoints[goal]['points']
                special = checkpoints[goal].get('special')
                if special:
                    self.specials.append(special)

    def _AI_control(self):
        f, l, r = self.simulation.sensor_check_on_track(self.rect.center, self.direction, Car.LOOK).values()
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