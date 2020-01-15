import pygame

from src.car import Car


class Game:
    FRAMERATE = 60

    def __init__(self):
        self._running = True
        self._display_surf = None
        self._bg = None
        self.size = self.width, self.height = 840, 600
        self.clock = pygame.time.Clock()
        self.groups = {}

    def _init(self):
        self._running = True

        pygame.init()
        self.bg = pygame.image.load('track.png')
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._display_surf.blit(self.bg, (0,0))

        self.player = Car()
        self.groups['cars'] = pygame.sprite.Group([self.player])

    def on_event(self, event):
        # print(event)
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        keystate = pygame.key.get_pressed()
        delta_vertical = (keystate[pygame.K_DOWN]-keystate[pygame.K_UP])
        delta_horizontal = (keystate[pygame.K_RIGHT]-keystate[pygame.K_LEFT])

        if keystate[pygame.K_UP]:
            self.player.accelerate(1)
        if keystate[pygame.K_DOWN]:
            self.player.accelerate(-1)
        if keystate[pygame.K_RIGHT]:
            self.player.steer(-1)
        if keystate[pygame.K_LEFT]:
            self.player.steer(1)

        for group in self.groups.values():
            group.update()

        for group in self.groups.values():
            group.clear(self._display_surf, self.bg)
            group.draw(self._display_surf)

        pygame.draw.line(self._display_surf, 234, [100,100], [100,100]+self.player.direction*100)

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
