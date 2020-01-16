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

        self.player = Car(self)
        self.AIs = [Car(self, True) for _ in range(3)]#[Car() for _ in range(100)]
        self.groups['cars'] = pygame.sprite.Group([self.player, *self.AIs])

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
                    if pixel[0]:
                        to_go[i] = False
                        dist[i] = d
                except IndexError:
                    continue

        return dist