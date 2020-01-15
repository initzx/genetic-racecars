import pygame


class Car(pygame.sprite.Sprite):
    WIDTH = 10
    HEIGHT = 15
    COLOR = 234

    FRICTION = 0.05
    ACCELERATION = 1.5
    MAX_ACCEL = 5
    MAX_SPEED = 5
    STEERING = 3

    def __init__(self, *groups):
        super().__init__(*groups)
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
        print(self.speed, self.accel)

        if self.speed.length() != 0:
            friction = self.speed*-Car.FRICTION
            self.accel += friction.normalize()
            self.speed = self.speed.normalize()*max(-Car.MAX_SPEED, min(self.speed.length(), Car.MAX_SPEED))

        self.speed += self.accel
        self.accel *= 0
        self.rect.move_ip(self.speed)
