import pygame


class Game:
    FRAMERATE = 60

    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.weight, self.height = 840, 600
        self.clock = pygame.time.Clock()
        self.x = 50

    def _init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True

    def on_event(self, event):
        # print(event)
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        self._display_surf.fill(pygame.Color(255, 255, 255))
        self.x += 1
        pygame.draw.rect(self._display_surf, 0, pygame.Rect((50, self.x), (50, 50)))

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
