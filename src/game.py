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
        self.max_ai_loop_time = 10
        self.groups = {}
        self.font = None
        self.starting_line = [(360, 80), (360, 160)]
        self.finish_line = [(350, 80), (350, 160)]

        self.all_time_best = [0, None]
        self.best_AIs = []
        self.goals = {
            'start': {'coords': [(360, 80), (360, 160)], 'points': 10},
            'finish': {'coords': [(350, 80), (350, 160)], 'points': 60},
            'checkpoints': {
                0: {'coords': [(540, 230), (630, 230)], 'points': 50},
                1: {'coords': [(600, 450), (650, 523)], 'points': 10},
                2: {'coords': [(175, 300), (250, 260)], 'points': 50},
                3: {'coords': [(450, 330), (450, 415)], 'points': 120},
                4: {'coords': [(263, 500), (263, 580)], 'points': 20, 'special': 'speed'}
            }
        }

    def _init(self):
        self._running = True

        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont('Ubuntu', 15)
        self.bg = pygame.image.load('track2.png')
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._display_surf.blit(self.bg, (0, 0))

        self.player = Car(self, None)
        self.AIs = [Car(self, AI([4, 4])) for _ in range(20)] #[Car() for _ in range(100)] []
        self.groups['players'] = pygame.sprite.Group([self.player])
        self.groups['cars'] = pygame.sprite.Group([self.player, *self.AIs])
        self.groups['AIs'] = pygame.sprite.Group(self.AIs)
        self.groups['text'] = pygame.sprite.Group()

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
        if keystate[pygame.K_SPACE]:
            for ai in self.AIs:
                ai.die()

        self.groups['cars'].update()
        self.groups['cars'].clear(self._display_surf, self.bg)
        self.groups['cars'].draw(self._display_surf)

        self.draw_goals()
        self.select_new_gen()
        self.draw_stats()

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
                    if pixel == (255, 255, 255, 255):
                        to_go[i] = False
                        dist[i] = d
                except IndexError:
                    continue
        return dist

    def draw_stats(self):
        self._display_surf.fill((255, 255, 255), pygame.Rect(700, 30, 100, 100))
        self._display_surf.fill((255, 255, 255), pygame.Rect(10, 30, 100, 100))

        self._display_surf.blit(self.font.render('Top 5 best cars', True, (0, 0, 0)), (700, 30))
        self._display_surf.blit(self.font.render('All time best', True, (0, 0, 0)), (10, 30))
        self._display_surf.blit(self.font.render(f'{self.all_time_best[0]}', True, self.all_time_best[1].color.rgb if self.all_time_best[1] else (0, 0, 0)), (10, 50))

        for i in range(min(len(self.best_AIs), 5)):
            text = self.font.render(f'{i+1}. {self.best_AIs[i].fitness}', True, self.best_AIs[i].color.rgb)
            self._display_surf.blit(text, (700, 30+(i+1)*15))

    def draw_goals(self):
        goals = [self.goals['start'], self.goals['finish'], *self.goals['checkpoints'].values()]
        for goal in goals:
            coords = goal['coords']
            pygame.draw.line(self._display_surf, 200, coords[0], coords[1])

    def select_new_gen(self):
        if time.time()-self.start > self.max_ai_loop_time:
            for ai in self.AIs:
                ai.die()

        if self.groups['AIs']:
            return

        self.best_AIs = sorted(self.AIs, key=lambda ai: ai.fitness, reverse=True)[:6]
        best_AI = self.best_AIs[0]
        if best_AI.fitness > self.all_time_best[0]:
            self.all_time_best = [best_AI.fitness, best_AI]

        mating_pool = [(ai, ai.fitness) for ai in self.best_AIs]
        # if self.all_time_best[1]:
        #     mating_pool.append((self.all_time_best[1], self.all_time_best[0]))

        random.shuffle(mating_pool)

        new_gen = []
        for _ in range(len(self.AIs)):
            partner_1 = self.select_random_cumulative(mating_pool)
            partner_2 = self.select_random_cumulative(mating_pool)
            child = Car.cross_over(self, partner_1, partner_2)
            new_gen.append(child)

        self.AIs = new_gen
        self.groups['AIs'].add(*new_gen)
        self.groups['cars'].add(*new_gen)
        self.start = time.time()

    def select_random_cumulative(self, pool):
        max_val = sum(i[1] for i in pool)
        selected = random.random()*max_val

        c = 0
        for cand, val in pool:
            c += val
            if c >= selected:
                return cand

