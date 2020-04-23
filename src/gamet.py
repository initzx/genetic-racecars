import random
import time

import neat
import pygame
import pygame_gui

from src.car import Car
from src.menu import SideMenu
from src.simulation import Simulation


class Game:
    FRAMERATE = 60
    AI_COUNT = 20

    def __init__(self):
        self.display_surf = None
        self._bg = None
        self.size = self.width, self.height = 1200, 600
        self.clock = pygame.time.Clock()
        self.start = time.time()
        self.max_ai_loop_time = 20
        self.starting_line = [(360, 80), (360, 160)]
        self.finish_line = [(350, 80), (350, 160)]

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
        self._stop_simulation = False
        pygame.init()
        pygame.font.init()

        self._bg = pygame.image.load('./tracks/track2.png')
        self.display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.display_surf.blit(self._bg, (0, 0))

        self.neat_config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         'config-feedforward')
        self.simulation = Simulation(self.display_surf, self._bg, self.neat_config, self.goals)
        self.simulation.start_generation()

        # self.side_menu = SideMenu(self)
        self.manager = pygame_gui.UIManager(self.size)
        self.kill_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 275), (100, 30)),
                                                     text='Kill all',
                                                     manager=self.manager)
        self.start_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 305), (100, 30)),
                                                     text='Start',
                                                     manager=self.manager)
        self.stop_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 335), (100, 30)),
                                                     text='Stop',
                                                     manager=self.manager)

    def check_events(self):
        for event in pygame.event.get():
            self.on_event(event)

    def on_event(self, event):
        # print(event)
        if event.type == pygame.QUIT:
            self._running = False

        elif event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.kill_btn:
                    self.simulation.kill_all()
                elif event.ui_element == self.stop_btn:
                    self.simulation.reset_population()
                    self._stop_simulation = True
                elif event.ui_element == self.start_btn:
                    if self._stop_simulation:
                        self._stop_simulation = False
                        self.simulation.start_generation()

        self.manager.process_events(event)

    def on_loop(self):
        time_delta = self.clock.tick(Game.FRAMERATE) / 1000

        self.manager.update(time_delta)
        self.manager.draw_ui(self.display_surf)

        self.simulation.update()
        if not self.simulation.generation_over or self._stop_simulation:
            return

        self.simulation.reproduce()
        self.simulation.start_generation()

    def on_cleanup(self):
        pygame.quit()

    def run(self):
        self._init()

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)

            self.on_loop()

            pygame.display.update()

        self.on_cleanup()