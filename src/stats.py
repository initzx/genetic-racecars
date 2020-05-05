from neat.math_util import mean
from neat.reporting import BaseReporter
from neat.six_util import itervalues


class StatsReporter(BaseReporter):
    def __init__(self):
        self.last_stats = {
            'avg': 0,
            'max_all_time': 0,
            'max': 0,
            'generation': 0,
        }

    def start_generation(self, generation):
        self.last_stats['generation'] = generation

    def end_generation(self, config, population, species_set):
        pass

    def post_evaluate(self, config, population, species, best_genome):
        fitnesses = [c.fitness for c in itervalues(population)]
        self.last_stats['avg'] = mean(fitnesses)
        self.last_stats['max'] = best_genome.fitness
        if best_genome.fitness > self.last_stats['max_all_time']:
            self.last_stats['max_all_time'] = best_genome.fitness

    def post_reproduction(self, config, population, species):
        pass

    def complete_extinction(self):
        pass

    def found_solution(self, config, generation, best):
        pass

    def species_stagnant(self, sid, species):
        pass

    def info(self, msg):
        pass