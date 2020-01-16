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

    def __init__(self, game, AI_control=False, *groups):
        super().__init__(*groups)
        self.game = game
        self.AI = AI([3, 4]) if AI_control else None
        self.image = self.original = pygame.Surface([Car.HEIGHT, Car.WIDTH])
        self.image.fill(Car.COLOR)
        self.image.set_colorkey((255, 0, 0))

        self.rect = self.image.get_rect(center=(100, 100))
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

        if self.speed.length() != 0:
            friction = self.speed*-Car.FRICTION
            self.accel += friction.normalize()
            self.speed = self.speed.normalize()*max(-Car.MAX_SPEED, min(self.speed.length(), Car.MAX_SPEED))

        self.speed += self.accel
        self.accel *= 0
        self.rect.move_ip(self.speed)

    def _AI_control(self):
        detection = self.game.sensor_check_on_track(self.rect.center, self.direction)
        control = self.AI.feedforward_la(np.array([*detection.values()]))
        print(control)

