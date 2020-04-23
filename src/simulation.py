import time

import neat
import pygame
from neat import CompleteExtinctionException
from neat.six_util import iteritems

from src.car import Car


class Simulation:

    def __init__(self, surf, map, neat_config, goals):
        self.surf = surf
        self.map = map
        self.neat_config = neat_config
        self.goals = goals
        self._running = False
        self.start = 0

        self.population = neat.Population(self.neat_config)
        self.population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        self.population.add_reporter(stats)

        self.cars = pygame.sprite.Group()

    @property
    def generation_over(self):
        if time.time() - self.start > 5:
            self.kill_all()

        if not self.cars:
            return True

        return False

    def kill_all(self):
        for car in self.cars:
            car.die()

    def reset_population(self):
        self.kill_all()
        self.population = neat.Population(self.neat_config)

    def update(self):
        self.update_cars()
        self.update_goals()

    def update_cars(self):
        self.cars.update()
        self.cars.clear(self.surf, self.map)
        self.cars.draw(self.surf)

    def update_goals(self):
        goals = [self.goals['start'], self.goals['finish'], *self.goals['checkpoints'].values()]
        for goal in goals:
            coords = goal['coords']
            pygame.draw.line(self.surf, 200, coords[0], coords[1])

    def start_generation(self):
        self.cars.add([Car(self, genome) for genome_id, genome in list(iteritems(self.population.population))])
        self.start = time.time()

    def reproduce(self):
        self.population.population = self.population.reproduction.reproduce(self.population.config,
                                                                            self.population.species,
                                                                            self.population.config.pop_size,
                                                                            self.population.generation)

        if not self.population.species.species:
            self.population.reporters.complete_extinction()

            # If requested by the user, create a completely new population,
            # otherwise raise an exception.
            if not self.population.config.reset_on_extinction:
                raise CompleteExtinctionException()

            self.population = self.population.reproduction.create_new(self.population.config.genome_type,
                                                                      self.population.config.genome_config,
                                                                      self.population.config.pop_size)
        # Divide the new population into species.
        self.population.species.speciate(self.population.config, self.population.population, self.population.generation)

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
                landed = pos + to_go[i] * d
                landed_rounded = round(landed[0]), round(landed[1])
                try:
                    pixel = self.surf.get_at(landed_rounded)
                    if pixel == (255, 255, 255, 255):
                        to_go[i] = False
                        dist[i] = d
                except IndexError:
                    continue
        return dist
