import random
import time

import pygame

from src.AI import AI
from src.car import Car


class Game:
    FRAMERATE = 60

    def __init__(self):
        self._running = True
        self._display_surf = None
        self._bg = None
        self.size = self.width, self.height = 840, 600
        self.clock = pygame.time.Clock()
        self.start = time.time()
        self.max_ai_loop_time = 5
        self.groups = {}

        self.starting_line = [(400, 80), (400, 160)]
        self.finish_line = [(350, 80), (350, 160)]

    def _init(self):
        self._running = True

        pygame.init()
        self.bg = pygame.image.load('track.png')
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._display_surf.blit(self.bg, (0, 0))

        self.player = Car(self, None)
        self.AIs = []#[Car(self, AI([3, 4])) for _ in range(20)]#[Car() for _ in range(100)]
        self.groups['players'] = pygame.sprite.Group([self.player])
        self.groups['cars'] = pygame.sprite.Group([self.player, *self.AIs])
        self.groups['AIs'] = pygame.sprite.Group(self.AIs)

    def on_event(self, event):
        # print(event)
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        keystate = pygame.key.get_pressed()

        if keystate[pygame.K_UP]:
            self.player.accelerate(1)
        if keystate[pygame.K_DOWN]:
            self.player.accelerate(-1)
        if keystate[pygame.K_RIGHT]:
            self.player.steer(-1)
        if keystate[pygame.K_LEFT]:
            self.player.steer(1)

        self.groups['cars'].update()
        self.groups['cars'].clear(self._display_surf, self.bg)
        self.groups['cars'].draw(self._display_surf)

        self.draw_start_finish()
        self.select_new_gen()

    def on_cleanup(self):
        pygame.quit()

    def run(self):
        self._init()

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)

            self.on_loop()

            pygame.display.update()
            self.clock.tick(Game.FRAMERATE)

        self.on_cleanup()

    def sensor_check_on_track(self, pos, facing, stop=100):
        facing = facing.normalize()
        left_looking = facing.rotate(-45)
        right_looking = facing.rotate(45)
        to_go = {"f": facing, "l": left_looking, "r": right_looking}
        dist = {"f": stop, "l": stop, "r": stop}

        for d in range(stop):
            for i in to_go:
                if not to_go[i]:
                    continue
                landed = pos+to_go[i]*d
                landed_rounded = round(landed[0]), round(landed[1])
                try:
                    pixel = self._display_surf.get_at(landed_rounded)
                    if pixel[0]:
                        to_go[i] = False
                        dist[i] = d
                except IndexError:
                    continue
        return dist

    def draw_start_finish(self):
        pygame.draw.line(self._display_surf, 200, self.starting_line[0], self.starting_line[1])
        pygame.draw.line(self._display_surf, 200, self.finish_line[0], self.finish_line[1])

    def select_new_gen(self):
        if time.time()-self.start > self.max_ai_loop_time:
            for ai in self.AIs:
                ai.die()

        if self.groups['AIs']:
            return

        best_AIs = sorted(self.AIs, key=lambda ai: ai.alive_time, reverse=True)
        mating_pool = {ai.alive_time: ai for ai in best_AIs[:5]}
        new_gen = []
        for _ in range(len(self.AIs)):
            partner_1 = self.select_random_cumulative(mating_pool)
            partner_2 = self.select_random_cumulative(mating_pool)
            new_gen.append(Car.cross_over(self, partner_1, partner_2))

        self.AIs = new_gen
        self.groups['AIs'].add(*new_gen)
        self.groups['cars'].add(*new_gen)

    def select_random_cumulative(self, pool):
        max_val = sum(pool.keys())
        selected = random.random()*max_val

        c = 0
        for val, cand in pool.items():
            c += val
            if c >= selected:
                return cand

