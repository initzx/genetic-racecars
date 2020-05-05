import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UIHorizontalSlider, UILabel, UIDropDownMenu, UIButton

options = {
    'Default': 'checkpoints',
    'Starting Line': 'start',
    'Finish Line': 'finish',
}


class CheckPoint(UIWindow):
    def __init__(self, rect, ui_manager, on_save):
        super().__init__(rect, ui_manager,
                         window_display_title='Choose checkpoint type',
                         object_id='#everything_window',
                         resizable=True)
        self.on_save = on_save

        self.type_text = UILabel(pygame.Rect((20, 50), (150, 25)),
                                 'Checkpoint Type',
                                 self.ui_manager,
                                 container=self)

        self.cp_type_select = UIDropDownMenu(options.keys(),
                                             'Default',
                                             pygame.Rect((250, 50), (140, 25)),
                                             self.ui_manager,
                                             container=self)

        self.slider_text = UILabel(pygame.Rect((20, 100),
                                               (150, 25)),
                                   'Checkpoint Point',
                                   self.ui_manager,
                                   container=self)

        self.point_slider = UIHorizontalSlider(
            pygame.Rect((250, 100), (140, 25)),
            50.0,
            (-50, 100.0),
            self.ui_manager,
            container=self)

        self.slider_label = UILabel(pygame.Rect((400, 100),
                                                (27, 25)),
                                    str(int(self.point_slider.get_current_value())),
                                    self.ui_manager,
                                    container=self)
        self.save_button = UIButton(pygame.Rect((300, 150),
                                                (60, 25)),
                                    'Save',
                                    self.ui_manager,
                                    object_id='#everything_button',
                                    container=self
                                    )

    def update(self, time_delta):
        super().update(time_delta)

        if self.alive() and self.point_slider.has_moved_recently:
            self.slider_label.set_text(str(int(self.point_slider.get_current_value())))

    def process_event(self, event: pygame.event.Event) -> bool:
        processed = super().process_event(event)

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.save_button:
                self.on_save(self.point_slider.get_current_value(), options[self.cp_type_select.selected_option])
                self.kill()
