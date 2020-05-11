import time

import neat
import pygame
from neat import CompleteExtinctionException
from neat.six_util import iteritems, itervalues

from src.car import Car
from src.stats import StatsReporter


class Simulation:

    def __init__(self, map, neat_config, map_config):
        self.map = map
        self.neat_config = neat_config
        self.map_config = map_config
        self._running = False
        self.start = 0
        self.cars = pygame.sprite.Group()
        self.reset_population()

    @property
    def starting_pos(self):
        a, b = self.map_config.checkpoints['start']['coords']
        return (a[0]+b[0])/2+5, (a[1]+b[1])/2,

    @property
    def generation_over(self):
        if time.time() - self.start > self.map_config.max_loop_time:
            self.kill_all()

        if not self.cars:
            return True

        return False

    @property
    def stats(self):
        return self.stats_reporter.last_stats

    def kill_all(self):
        for car in self.cars:
            car.die()

    def reset_population(self):
        self.kill_all()
        self.population = neat.Population(self.neat_config)
        self.stats_reporter = StatsReporter()
        self.population.add_reporter(self.stats_reporter)

    def update(self):
        self.update_cars()
        self.update_goals()

    def update_cars(self):
        self.cars.update()
        # self.cars.clear(self.surf, self.map)
        self.cars.draw(self.map)

    def update_goals(self):
        checkpoints = self.map_config.checkpoints
        goals = [*checkpoints['checkpoints'].values()]

        pygame.draw.line(self.map, (0,255,0), checkpoints['start']['coords'][0],  checkpoints['start']['coords'][1], 2)
        pygame.draw.line(self.map, (255,0,0), checkpoints['finish']['coords'][0],  checkpoints['finish']['coords'][1], 2)

        for goal in goals:
            coords = goal['coords']
            pygame.draw.line(self.map,  (0, 0, 255), coords[0], coords[1], 2)

    def start_generation(self):
        self.population.reporters.start_generation(self.population.generation)
        self.cars.add([Car(self, self.map_config.car_config, genome) for genome_id, genome in list(iteritems(self.population.population))])
        self.start = time.time()

    def reproduce(self):
        # Koden her er taget fra NEAT-Python

        best = None

        for g in itervalues(self.population.population):
            if best is None or g.fitness > best.fitness:
                best = g
        self.population.reporters.post_evaluate(self.neat_config, self.population.population, self.population.species, best)
        self.population.reporters.end_generation(self.neat_config, self.population.population, self.population.species)
        self.population.generation += 1
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

            self.population = self.population.reproduction.create_new(self.neat_config.genome_type,
                                                                      self.neat_config.genome_config,
                                                                      self.neat_config.pop_size)
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
                    pixel = self.map.get_at(landed_rounded)
                    if pixel == (255, 255, 255, 255):
                        to_go[i] = False
                        dist[i] = d
                except IndexError:
                    continue
        return dist
