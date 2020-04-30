import time

import neat
import pygame
import pygame_gui
from pygame_gui.core.utility import create_resource_path

from src.map_loader import MapConfig
from src.paint_modes import PaintMode
from src.pop_up import CheckPoint
from src.simulation import Simulation

default_map_config = MapConfig(
    map= pygame.image.load('./tracks/track2.png'),
    checkpoints={
            'start': {'coords': [(360, 80), (360, 160)], 'points': 10},
            'finish': {'coords': [(350, 80), (350, 160)], 'points': 60},
            'checkpoints': {
            #      0: {'coords': [(540, 230), (630, 230)], 'points': 20, 'special': 'slowness'},
            #      1: {'coords': [(600, 450), (650, 523)], 'points': 20},
            #      2: {'coords': [(175, 300), (250, 260)], 'points': 50},
            #      3: {'coords': [(450, 330), (450, 415)], 'points': 50},
            #      4: {'coords': [(263, 500), (263, 580)], 'points': 100, 'special': 'speed'}
             }
        },
    spawn_point=(421, 115),
    cars=10,
    max_loop_time=20
)


class Game:
    FRAMERATE = 60
    AI_COUNT = 20
    SIMUL_SURF_COORDS = (0, 0)

    def __init__(self):

        self.display_surf = None
        self.size = self.width, self.height = 1200, 600
        self.clock = pygame.time.Clock()
        self.start = time.time()
        self.last_press_pos = None
        self.map_config = default_map_config
        self._bg = default_map_config.map
        self.neat_config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                              neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                              'config-feedforward')

    def _init(self):
        pygame.init()
        pygame.font.init()

        self._stopped = False
        self._stop_simulation = False
        self._paint_mode = False
        self._load_mode = False

        self._init_surfs()
        self._init_simul()
        self._init_controls()

    def _init_surfs(self):
        self.display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.simul_surf = pygame.Surface(self.map_config.map.get_size())
        self.control_surf = pygame.Surface(
            (self.display_surf.get_width() - self.simul_surf.get_width(), self.simul_surf.get_height()))

    def _init_simul(self):
        self.simulation = Simulation(self.simul_surf, self.neat_config, self.map_config)
        self.simulation.start_generation()

    def _init_controls(self):
        # self.side_menu = SideMenu(self)
        self.manager = pygame_gui.UIManager(self.display_surf.get_size())

        self.kill_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((850, 70), (100, 30)),
                                                     text='Kill all',
                                                     manager=self.manager,
                                                     )
        self.start_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((850, 30), (100, 30)),
                                                      text='Start',
                                                      manager=self.manager)
        self.stop_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1000, 30), (100, 30)),
                                                     text='Stop',
                                                     manager=self.manager)

        self.selected_press_mode = None
        self.paint_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1000, 70), (100, 30)),
                                                      text='Draw',
                                                      manager=self.manager
                                                      )

        self.erase_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1000, 100), (100, 30)),
                                                      text='Erase',
                                                      manager=self.manager
                                                      )
        self.new_checkpoint = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(1000, 130, 100, 30),
                                                           text='New Checkpoint',
                                                           manager=self.manager,
                                                           )
        self.load_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(-200, -60, 100, 30),
                                                        text='Load Map',
                                                        manager=self.manager,
                                                        anchors={'left': 'right',
                                                                 'right': 'right',
                                                                 'top': 'bottom',
                                                                 'bottom': 'bottom'})

        self.save_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(-300, -60, 100, 30),
                                                        text='Save Map',
                                                        manager=self.manager,
                                                        anchors={'left': 'right',
                                                                 'right': 'right',
                                                                 'top': 'bottom',
                                                                 'bottom': 'bottom'})

        self.file_dialog = None

        self.game_mode_buttons = [self.stop_btn, self.kill_btn]
        self.paint_mode_buttons = [self.start_btn, self.paint_btn, self.erase_btn, self.new_checkpoint]
        self.load_mode_buttons = [self.save_button, self.load_button]
        self.game_mode()

    def paint_mode(self):
        self._paint_mode = True
        for b in self.game_mode_buttons:
            b.disable()
        for b in self.paint_mode_buttons:
            b.enable()
        for b in self.load_mode_buttons:
            b.enable()

    def game_mode(self):
        self._paint_mode = False
        for b in self.paint_mode_buttons:
            b.disable()
        for b in self.game_mode_buttons:
            b.enable()
        for b in self.load_mode_buttons:
            b.disable()

    def disable_load_mode_buttons(self):
        for b in self.load_mode_buttons:
            b.disable()

    def enable_load_mode_buttons(self):
        for b in self.load_mode_buttons:
            b.enable()

    def load_map(self):
        self.disable_load_mode_buttons()
        self.file_dialog = pygame_gui.windows.UIFileDialog(pygame.Rect(160, 50, 440, 500),
                                                           self.manager,
                                                           window_title='Load Map',
                                                           initial_file_path='tracks/',
                                                           allow_existing_files_only=True)

    def save_map(self, path):
        pygame.image.save(self._bg, path)
        self.file_dialog = pygame_gui.windows.UIMessageWindow(
            pygame.Rect(500, 200, 100, 50),
            html_message='Map saved!',
            manager=self.manager,
            window_title=''
        )

    def add_checkpoint(self, coords):
        def inner(points, type):
            if type != 'checkpoints':
                self.map_config.checkpoints[type] = {'coords': coords, 'points': points}
            else:
                next_index = max(self.map_config.checkpoints['checkpoints'].keys())+1 if self.map_config.checkpoints['checkpoints'] else 0
                self.map_config.checkpoints['checkpoints'][next_index] = {'coords': coords, 'points': points}
                print(self.map_config.checkpoints['checkpoints'])
        return inner

    def paint_update(self, event):
        px, py = pygame.mouse.get_pos()
        if self.last_press_pos:
            pygame.draw.line(self.simul_surf, (0, 0, 255), self.last_press_pos, (px, py), 2)

        if pygame.mouse.get_pressed() == (1, 0, 0):
            if self.selected_press_mode == PaintMode.DRAW:
                pygame.draw.circle(self._bg, 0, (px, py), 20)
            elif self.selected_press_mode == PaintMode.ERASE:
                pygame.draw.circle(self._bg, (255, 255, 255), (px, py), 20)

        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        if pygame.mouse.get_pressed() == (1, 0, 0):
            if self.selected_press_mode == PaintMode.CHECKPOINT:
                if self.last_press_pos:
                    # pygame.draw.line(self._bg, (0, 0, 255), self.last_press_pos, (px, py), 2)
                    CheckPoint(pygame.Rect((10, 10), (500, 280)), self.manager, self.add_checkpoint([self.last_press_pos, (px, py)]))
                    self.selected_press_mode = None
                    self.last_press_pos = None
                else:
                    self.last_press_pos = (px, py)
        elif pygame.mouse.get_pressed() == (0, 0, 1):
            self.last_press_pos = None

    def check_events(self):
        for event in pygame.event.get():
            self.on_event(event)

    def on_event(self, event):
        # print(event)

        if self._paint_mode:
            self.paint_update(event)

        if event.type == pygame.QUIT:
            self._stopped = True

        elif event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.kill_btn:
                    self.simulation.kill_all()
                elif event.ui_element == self.stop_btn:
                    self.simulation.reset_population()
                    self._stop_simulation = True
                    self.paint_mode()
                elif event.ui_element == self.start_btn:
                    if self._stop_simulation:
                        self.game_mode()
                        self._stop_simulation = False
                        self.simulation.start_generation()

                elif event.ui_element == self.paint_btn:
                    self.selected_press_mode = PaintMode.DRAW
                    self.paint_btn.disable()
                    self.erase_btn.enable()
                elif event.ui_element == self.erase_btn:
                    self.selected_press_mode = PaintMode.ERASE
                    self.paint_btn.enable()
                    self.erase_btn.disable()

                elif event.ui_element == self.new_checkpoint:
                    self.selected_press_mode = PaintMode.CHECKPOINT

                elif event.ui_element == self.load_button:
                    self.load_map()
                elif event.ui_element == self.save_button:
                    self.save_map('./tracks/test.png')

                    # self.disable_load_mode_buttons()
            elif event.user_type == pygame_gui.UI_WINDOW_CLOSE:
                if event.ui_element == self.file_dialog:
                    self.enable_load_mode_buttons()
                    self.file_dialog = None

            elif event.user_type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
                # try:
                image_path = create_resource_path(event.text)
                self._bg = pygame.image.load(image_path)

        self.manager.process_events(event)

    def draw_stats(self, stats):
        pass
        # print(stats)

    def on_loop(self):
        time_delta = self.clock.tick(Game.FRAMERATE) / 1000

        self.display_surf.blit(self.simul_surf, Game.SIMUL_SURF_COORDS)
        self.display_surf.blit(self.control_surf, (self.simul_surf.get_width(), 0))
        self.simul_surf.blit(self._bg, (0, 0))

        self.manager.update(time_delta)
        self.manager.draw_ui(self.display_surf)

        # if self._paint_mode:
        #     self.paint_update()

        self.simulation.update()
        self.draw_stats(self.simulation.stats)

        if not self.simulation.generation_over or self._stop_simulation:
            return

        self.simulation.reproduce()
        self.simulation.start_generation()

    def on_cleanup(self):
        pygame.quit()

    def run(self):
        self._init()

        while not self._stopped:
            for event in pygame.event.get():
                self.on_event(event)

            self.on_loop()
            pygame.display.update()

        self.on_cleanup()
