import random
import time

import neat
import pygame

from src.car import Car


class Game:
    FRAMERATE = 60
    AI_COUNT = 20

    def __init__(self):
        self._running = True
        self._display_surf = None
        self.map = None
        self.size = self.width, self.height = 1200, 600
        self.clock = pygame.time.Clock()
        self.start = time.time()
        self.max_ai_loop_time = 20
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
                0: {'coords': [(540, 230), (630, 230)], 'points': 20, 'special': 'slowness'},
                1: {'coords': [(600, 450), (650, 523)], 'points': 20},
                2: {'coords': [(175, 300), (250, 260)], 'points': 50},
                3: {'coords': [(450, 330), (450, 415)], 'points': 50},
                4: {'coords': [(263, 500), (263, 580)], 'points': 100, 'special': 'speed'}
            }
        }

    def _init(self):
        self._running = True

        self.neat_config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         'config-feedforward')

        self.population = neat.Population(self.neat_config)
        self.population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        self.population.add_reporter(stats)

        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont('Ubuntu', 15)
        self.map = pygame.image.load('./tracks/track2.png')
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._display_surf.blit(self.map, (0, 0))

        self.groups['cars'] = pygame.sprite.Group()
        self.groups['text'] = pygame.sprite.Group()

    def check_events(self):
        for event in pygame.event.get():
            self.on_event(event)

    def check_stop(self):
        if not self.groups['cars'] or time.time()-self.start > self.max_ai_loop_time:
            for car in self.AIs:
                car.die()
            self._running = False

    def on_event(self, event):
        # print(event)
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        self.check_keystate()
        self.draw_cars()
        self.draw_goals()
        self.check_stop()
        # self.select_new_gen()
        # self.draw_stats()
        # self._running = False

    def on_cleanup(self):
        pygame.quit()

    def simulate(self, genomes, config):
        self.AIs = [Car(self, genome) for genome_id, genome in genomes]
        self.groups['cars'].add(self.AIs)
        self.start = time.time()

        self._running = True
        while self._running:
            self.check_events()
            self.on_loop()

            pygame.display.update()
            self.clock.tick(Game.FRAMERATE)

    def run(self):
        self._init()
        self.population.run(self.simulate, 50)
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

    def check_keystate(self):
        keystate = pygame.mouse.get_pressed()
        if keystate[0]:
            for ai in self.AIs:
                ai.die()

    def draw_cars(self):
        self.groups['cars'].update()
        self.groups['cars'].clear(self._display_surf, self.map)
        self.groups['cars'].draw(self._display_surf)

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
