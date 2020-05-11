import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UIHorizontalSlider, UILabel, UIDropDownMenu, UIButton

options = {
    'Normalt': 'checkpoints',
    'Startlinje': 'start',
    'Slutlinje': 'finish',
}


class CheckPoint(UIWindow):
    def __init__(self, rect, ui_manager, on_save):
        super().__init__(rect, ui_manager,
                         window_display_title='Vælg checkpoint type',
                         object_id='#everything_window',
                         resizable=True)
        self.on_save = on_save

        self.type_text = UILabel(pygame.Rect((20, 50), (150, 25)),
                                 'Checkpoint type',
                                 self.ui_manager,
                                 container=self)

        self.cp_type_select = UIDropDownMenu(options.keys(),
                                             'Normalt',
                                             pygame.Rect((250, 50), (140, 25)),
                                             self.ui_manager,
                                             container=self)

        self.slider_text = UILabel(pygame.Rect((20, 100),
                                               (150, 25)),
                                   'Checkpoint point',
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


class HelpText(UIWindow):
    def __init__(self, rect, manager):
        super().__init__(rect, manager)
        self.help_text = pygame_gui.elements.UITextBox(html_text=
"""
<p>Genetic racecars er et spil som omhandler nogle racerbiler der kører på en bane. Racerbilerne tjener point hver gang de kører over et mål eller checkpoint, og dem som har tjent flest point bliver valgt med en evolutionær algoritme til at videreføre deres gener til den næste generation. </p>
<p>Du kan optimere for simulationens parametre således at bilerne bliver bedre til at køre, og tilføje flere ruter ved at ændre på banen. Derudover kan du tilføje flere checkpoints med flere point for at gøre en rute mere foretrukken end en anden.</p>
<p>Banen har altid en <font color=#4CD656>startlinje</font> og en <font color=#FF6347>slutlinje</font>. En bil kan ikke køre over startlinjen medmindre de først har kørt over slutlinjen, ved overtrædelse af dette dør bilen. En bil tjener kun point ved at køre over de normale checkpoints en gang, men hvis bilen slutter dens tur rundt om banen (dvs. at den kører over slut- og startlinjen), kan den igen køre over de normale checkpoints for point igen. </p>
""",
                                                       relative_rect=pygame.Rect(-2, -2, rect.width-30, rect.height-50),
                                                       manager=manager,
                                                       container=self
                                                       )
