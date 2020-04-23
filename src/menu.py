import pygame
import pygame_gui


class SideMenu:
    def __init__(self, game):
        self.manager = pygame_gui.UIManager(game.dimensions)
        self.window_surf = game.display_surf

        self.hello_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 275), (100, 30)),
                                                         text='Kill all',
                                                         manager=self.manager)

    def update(self, time_delta):
        self.manager.update(time_delta)
        self.manager.draw_ui(self.window_surf)

    def process_events(self, event):
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.hello_button:
                    print('Hello World!')

        self.manager.process_events(event)
