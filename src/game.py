import time

import neat
import pygame
import pygame_gui
from pygame_gui.core.utility import create_resource_path

from src.paint_modes import PaintMode
from src.pop_up import CheckPoint, HelpText
from src.simulation import Simulation


class MapConfig:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


default_map_config = MapConfig(
    map=pygame.image.load('./tracks/track2.png'),
    checkpoints={
        'start': {'coords': [(360, 80), (360, 160)], 'points': 0},
        'finish': {'coords': [(350, 80), (350, 160)], 'points': 60},
        'checkpoints': {
            0: {'coords': [(486, 157), (486, 73)], 'points': 50.0}
        }
    },
    spawn_point=(421, 115),
    pop_size=50,
    max_loop_time=20,
    car_config={
        'friction': 0.9,
        'acceleration': 1.6,
        'max_speed': 5,
        'steering': 8,
        'look': 400
    }
)


class Game:
    FRAMERATE = 60
    AI_COUNT = 20
    SIMUL_SURF_COORDS = (0, 0)

    def __init__(self):

        self.display_surf = None
        self.size = self.width, self.height = 1500, 600
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
        self._paint_mode = True
        self._load_mode = False

        self._init_surfs()
        self._init_simul()
        self._init_controls()
        # self.game_mode()

    def _init_surfs(self):
        self.display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.simul_surf = pygame.Surface(self.map_config.map.get_size())
        self.control_surf = pygame.Surface((self.display_surf.get_width() - self.simul_surf.get_width(), self.simul_surf.get_height()))

    def _init_simul(self):
        self.simulation = Simulation(self.simul_surf, self.neat_config, self.map_config)
        self.simulation.start_generation()

    def _init_controls(self):
        # self.side_menu = SideMenu(self)
        self.manager = pygame_gui.UIManager(self.display_surf.get_size())
        HelpText(pygame.Rect((850, 30), (600, 400)), self.manager)
        # self.start_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((850, 30), (100, 30)),
        #                                               text='Start',
        #                                               manager=self.manager,
        #                                               tool_tip_text='Start simulationen'
        #                                               )
        self.kill_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((960, 30), (100, 30)),
                                                     text='Dræb alle',
                                                     manager=self.manager,
                                                     tool_tip_text='Dræb alle biler og start en ny generation'
                                                     )
        self.reset_population = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1070, 30), (100, 30)),
                                                     text='Genstart',
                                                     manager=self.manager,
                                                     tool_tip_text='Dræb alle biler og start populationen om igen'
                                                     )
        # self.stop_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((850, 70), (100, 30)),
        #                                              text='Stop',
        #                                              manager=self.manager,
        #                                              tool_tip_text='Stop simulationen øjeblikkeligt'
        #                                              )
        self.paint_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((960, 70), (100, 30)),
                                                      text='Tegn bane',
                                                      manager=self.manager,
                                                      tool_tip_text='Banen tegnes ved at trække musen over dele af simulationen'
                                                      )
        self.erase_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1070, 70), (100, 30)),
                                                      text='Slet bane',
                                                      manager=self.manager,
                                                      tool_tip_text='Banen slettes ved at trække musen over dele af simulationen'
                                                      )
        self.new_checkpoint = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1180, 70), (120, 30)),
                                                           text='Ny Checkpoint',
                                                           manager=self.manager,
                                                           tool_tip_text='Tilføj en ny checkpoint ved at klikke på 2 forskellige steder på banen, højre-klik for at annullere'
                                                           )

        pygame_gui.elements.UILabel(pygame.Rect((860, 120),
                                                (150, 19)),
                                    'Bil styringer',
                                    self.manager)

        self.friction_slider = pygame_gui.elements.UIHorizontalSlider(
                                                                    pygame.Rect((850, 150), (180, 30)),
                                                                    default_map_config.car_config['friction'],
                                                                    (0, 2),
                                                                    self.manager)
        pygame_gui.elements.UILabel(pygame.Rect((860, 153),
                                                                                (150, 19)),
                                                                                'Friktion',
                                                                                self.manager)

        self.accel_slider = pygame_gui.elements.UIHorizontalSlider(
                                                                    pygame.Rect((850, 180), (180, 30)),
                                                                    default_map_config.car_config['acceleration'],
                                                                    (0, 9),
                                                                    self.manager)
        pygame_gui.elements.UILabel(pygame.Rect((860, 183),
                                                                                (150, 19)),
                                                                                'Acceleration',
                                                                                self.manager)

        self.speed_slider = pygame_gui.elements.UIHorizontalSlider(
                                                                    pygame.Rect((850, 210), (180, 30)),
                                                                    default_map_config.car_config['max_speed'],
                                                                    (1, 9),
                                                                    self.manager)
        pygame_gui.elements.UILabel(pygame.Rect((860, 213),
                                                                                (150, 19)),
                                                                                'Maks hastighed',
                                                                                self.manager)

        self.steering_slider = pygame_gui.elements.UIHorizontalSlider(
                                                                    pygame.Rect((850, 240), (180, 30)),
                                                                    default_map_config.car_config['steering'],
                                                                    (0, 20),
                                                                    self.manager)
        pygame_gui.elements.UILabel(pygame.Rect((860, 243),
                                                                                (150, 19)),
                                                                                'Drejningsevne',
                                                                                self.manager)

        self.look_slider = pygame_gui.elements.UIHorizontalSlider(
                                                                    pygame.Rect((850, 270), (180, 30)),
                                                                    default_map_config.car_config['look'],
                                                                    (0, 600),
                                                                    self.manager)
        pygame_gui.elements.UILabel(pygame.Rect((860, 273),
                                                                                (150, 19)),
                                                                                'Syn afstand',
                                                                                self.manager)

        pygame_gui.elements.UILabel(pygame.Rect((1060, 120),
                                                (150, 19)),
                                    'Simulation settings',
                                    self.manager)
        self.pop_size_slider = pygame_gui.elements.UIHorizontalSlider(
                                            pygame.Rect((1050, 150), (180, 30)),
                                            default_map_config.pop_size,
                                            (2, 100),
                                            self.manager)
        self.pop_size_label = pygame_gui.elements.UILabel(pygame.Rect((1060, 153),
                                                                                (150, 19)),
                                                                                f'Biler: {default_map_config.pop_size}',
                                                                                self.manager)

        self.max_loop_time = pygame_gui.elements.UIHorizontalSlider(
                                            pygame.Rect((1050, 180), (180, 30)),
                                            default_map_config.max_loop_time,
                                            (1, 100),
                                            self.manager)
        self.max_loop_time_label = pygame_gui.elements.UILabel(pygame.Rect((1060, 183),
                                                                                (150, 19)),
                                                                                f'Gen. tid: {default_map_config.max_loop_time}',
                                                                                self.manager)

        self.selected_press_mode = None

        self.file_dialog = None
        self.control_surf.fill(self.manager.ui_theme.get_colour(None, None, 'dark_bg'))
        # self.game_mode_buttons = [self.stop_btn, self.kill_btn]
        # self.paint_mode_buttons =[]# [self.start_btn, self.paint_btn, self.erase_btn, self.new_checkpoint, self.reset_population]
        # self.load_mode_buttons = [self.save_button, self.load_button]

    def paint_mode(self):
        self._paint_mode = True
        for b in self.game_mode_buttons:
            b.disable()
        for b in self.paint_mode_buttons:
            b.enable()
        # for b in self.load_mode_buttons:
        #     b.enable()

    def game_mode(self):
        self._paint_mode = False
        for b in self.paint_mode_buttons:
            b.disable()
        for b in self.game_mode_buttons:
            b.enable()
    #     for b in self.load_mode_buttons:
    #         b.disable()
    #
    # def disable_load_mode_buttons(self):
    #     for b in self.load_mode_buttons:
    #         b.disable()
    #
    # def enable_load_mode_buttons(self):
    #     for b in self.load_mode_buttons:
    #         b.enable()
    #
    # def load_map(self):
    #     self.disable_load_mode_buttons()
    #     self.file_dialog = pygame_gui.windows.UIFileDialog(pygame.Rect(160, 50, 440, 500),
    #                                                        self.manager,
    #                                                        window_title='Load Map',
    #                                                        initial_file_path='tracks/',
    #                                                        allow_existing_files_only=True)
    #
    # def save_map(self, path):
    #     pygame.image.save(self._bg, path)
    #     self.file_dialog = pygame_gui.windows.UIMessageWindow(
    #         pygame.Rect(500, 200, 100, 50),
    #         html_message='Map saved!',
    #         manager=self.manager,
    #         window_title=''
    #     )

    def add_checkpoint(self, coords):
        def inner(points, type):
            if type != 'checkpoints':
                self.map_config.checkpoints[type] = {'coords': coords, 'points': points}
            else:
                next_index = max(self.map_config.checkpoints['checkpoints'].keys()) + 1 if self.map_config.checkpoints[
                    'checkpoints'] else 0
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
                    CheckPoint(pygame.Rect((10, 10), (500, 280)), self.manager,
                               self.add_checkpoint([self.last_press_pos, (px, py)]))
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
                elif event.ui_element == self.reset_population:
                    print('here')
                    self._stop_simulation = True
                # elif event.ui_element == self.stop_btn:
                #     # self.simulation.reset_population()
                #     self.simulation.kill_all()
                #     self._stop_simulation = True
                #     self.paint_mode()
                # elif event.ui_element == self.start_btn:
                #     if self._stop_simulation:
                #         self.game_mode()
                #         self._stop_simulation = False
                #         self.simulation.start_generation()

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

                # elif event.ui_element == self.load_button:
                #     self.load_map()
                # elif event.ui_element == self.save_button:
                #     self.save_map('./tracks/test.png')

                    # self.disable_load_mode_buttons()
            elif event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == self.friction_slider:
                    default_map_config.car_config['friction'] = self.friction_slider.get_current_value()
                elif event.ui_element == self.accel_slider:
                    default_map_config.car_config['acceleration'] = self.accel_slider.get_current_value()
                elif event.ui_element == self.speed_slider:
                    default_map_config.car_config['max_speed'] = self.speed_slider.get_current_value()
                elif event.ui_element == self.steering_slider:
                    default_map_config.car_config['steering'] = self.steering_slider.get_current_value()
                elif event.ui_element == self.look_slider:
                    default_map_config.car_config['look'] = int(self.look_slider.get_current_value())
                elif event.ui_element == self.pop_size_slider:
                    size = int(self.pop_size_slider.get_current_value())
                    default_map_config.pop_size = size
                    self.neat_config.pop_size = size
                    self.pop_size_label.set_text(f'Biler: {size}')
                elif event.ui_element == self.max_loop_time:
                    time = int(self.max_loop_time.get_current_value())
                    default_map_config.max_loop_time = time
                    self.max_loop_time_label.set_text(f'Gen. tid: {time}')

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
        if self.__dict__.get('stats'):
            self.stats.kill()

        self.stats = pygame_gui.elements.UITextBox(
f"""
<b>Generation: {stats['generation']}</b>
<br>
<p>Bedste point: {stats['max']:.0f}</p>
<p>Bedste point nogensinde: {stats['max_all_time']:.0f}</p>
<p>Population gennemsnit: {stats['avg']:.0f}</p>
""",
                  pygame.Rect((850, 300), (250, 200)),
                  manager=self.manager,
                  object_id="#text_box_2")
        # print(stats)

    def draw_surfaces(self):
        self.display_surf.blit(self.simul_surf, Game.SIMUL_SURF_COORDS)
        self.display_surf.blit(self.control_surf, (self.simul_surf.get_width(), 0))
        self.simul_surf.blit(self._bg, (0, 0))
        self.draw_stats(self.simulation.stats)

    def update_simul(self):
        self.simulation.update()

        if self._stop_simulation:
            self._stop_simulation = False
            self.simulation.reset_population()
            self.simulation.start_generation()
            return

        if not self.simulation.generation_over:
            return

        self.simulation.reproduce()
        self.simulation.start_generation()

    def on_loop(self):
        time_delta = self.clock.tick(Game.FRAMERATE) / 1000
        self.check_events()
        self.draw_surfaces()

        self.manager.update(time_delta)
        self.manager.draw_ui(self.display_surf)
        self.update_simul()

    def on_cleanup(self):
        pygame.quit()

    def run(self):
        self._init()

        while not self._stopped:
            self.on_loop()
            pygame.display.update()

        self.on_cleanup()
