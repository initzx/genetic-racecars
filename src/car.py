import time

import numpy as np
import pygame

from src.AI import AI


class Car(pygame.sprite.Sprite):
    WIDTH = 10
    HEIGHT = 15
    COLOR = 234

    FRICTION = 0.05
    ACCELERATION = 1.5
    MAX_ACCEL = 5
    MAX_SPEED = 5
    STEERING = 3

    def __init__(self, game, AI, *groups):
        super().__init__(*groups)
        self.game = game
        self.AI = AI
        self.alive = True
        self.alive_time = 0
        self.points = 0
        self.finishing_seq = [0, 1]
        self.goals = {1: game.starting_line, 0: game.finish_line}

        self.image = self.original = pygame.Surface([Car.HEIGHT, Car.WIDTH])
        self.image.fill(Car.COLOR)
        self.image.set_colorkey((255, 0, 0))

        self.rect = self.image.get_rect(center=(373, 115))
        self.accel = pygame.Vector2(0, 0)
        self.speed = pygame.Vector2(0, 0)
        self.direction = self.original_dir = pygame.Vector2(1, 0)
        self.angle = 0

    def accelerate(self, f_or_b):
        self.accel += f_or_b*self.direction*Car.ACCELERATION

    def steer(self, r_or_l):
        self.angle += r_or_l*Car.STEERING
        self.angle %= 360
        self.direction = self.original_dir.rotate(-self.angle)
        self.image = pygame.transform.rotate(self.original, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self, *args, **kwargs):
        if self.AI:
            self._AI_control()
        else:
            print(self.points)

        if self.speed.length() != 0:
            friction = self.speed*-Car.FRICTION
            self.accel += friction.normalize()
            self.speed = self.speed.normalize()*max(-Car.MAX_SPEED, min(self.speed.length(), Car.MAX_SPEED))

        self.speed += self.accel
        self.accel *= 0
        self.rect.move_ip(self.speed)

        if self.game.bg.get_at(self.rect.center)[0] == 255:
            self.die()

        next_goal = self.goals[self.finishing_seq[0]]
        wrong_goal = self.goals[self.finishing_seq[1]]
        car_line = [self.rect.center, self.rect.center+self.direction*20]

        if intersect(car_line, next_goal):
            self.points += 5
            self.finishing_seq.insert(len(self.finishing_seq), self.finishing_seq.pop(0))

        if intersect(car_line, wrong_goal):
            self.points = 0
            self.die()

    def _AI_control(self):
        detection = self.game.sensor_check_on_track(self.rect.center, self.direction)
        control = self.AI.feedforward_la(np.array([*detection.values()]))

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
        self.alive_time = time.time() - self.game.start

    @staticmethod
    def cross_over(game, mate1, mate2):
        child_AI = AI.cross_over(mate1.AI, mate2.AI)
        return Car(game, child_AI)

def ccw(A,B,C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

# Return true if line segments AB and CD intersect
def intersect(A, B):
    return ccw(A[0], B[0], B[1]) != ccw(A[1], B[0], B[1]) and ccw(A[0], A[1], B[0]) != ccw(A[0], A[1], B[1])