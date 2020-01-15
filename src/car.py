import pygame


class Car(pygame.sprite.Sprite):
    WIDTH = 40
    HEIGHT = 60
    COLOR = 234

    FRICTION = 0.05
    ACCELERATION = 1.5
    STEERING = 0.1

    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = self.original = pygame.Surface([Car.HEIGHT, Car.WIDTH])
        self.image.fill(Car.COLOR)
        self.image.set_colorkey((255, 0, 0))

        self.rect = self.image.get_rect(center=(100, 100))
        self.accel = pygame.Vector2(0, 0)
        self.speed = pygame.Vector2(0, 0)
        self.direction = pygame.Vector2(1, 0)
        self.angle = 0

    def accelerate(self, f_or_b):
        self.accel += f_or_b*self.direction*Car.ACCELERATION

    def steer(self, r_or_l):
        self.angle += 1 #(self.angle+r_or_l*Car.STEERING)%360
        self.direction.rotate_ip(self.angle)
        self.image = pygame.transform.rotate(self.original, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self, *args, **kwargs):
        print(self.direction, self.angle)

        if self.speed.length() != 0:
            friction = self.speed*-Car.FRICTION
            self.accel += friction.normalize()

        self.speed += self.accel
        self.accel *= 0
        self.rect.move_ip(self.speed)
