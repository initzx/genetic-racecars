import random

import numpy as np

ACTIVATION_SIGMOID = lambda x: 1.0 / (1.0 + np.exp(-x))


class AI:
    MUTATION_RATE = 0.05

    def __init__(self, dimensions, weights=None, biases=None, mutated=False):
        self.n_layers = len(dimensions)
        self.dimensions = dimensions
        self.weights = weights
        self.biases = biases
        self.mutated = mutated

        # the weights are matrices with dimensions of n_neurons(l) x n_neurons(l+1)
        # we index backwards (j, k) to optimize for matrix transformation
        if not weights:
            self.weights = [np.random.randn(j, k) for k, j in zip(dimensions[:-1], dimensions[1:])]

        if not biases:
            self.biases = [np.random.randn(k) for k in dimensions[1:]]

    def feedforward_la(self, activation):
        for b, w in zip(self.biases, self.weights):
            activation = np.dot(w, activation) + b  # a = f(w . a + b)
        return activation

    @staticmethod
    def cross_over(mate1, mate2):
        child_weights = AI.cross_over_trait(mate1.weights, mate2.weights)
        child_biases = AI.cross_over_trait(mate1.biases, mate2.biases)
        return AI(mate1.dimensions, child_weights, child_biases, True)

    @staticmethod
    def cross_over_trait(trait1, trait2):
        child_traits = []
        for t1, t2 in zip(trait1, trait2):
            f1 = t1.flatten()
            f2 = t2.flatten()

            split_at = random.randint(0, len(f1))
            child_chromosomes = []

            for i in range(len(f1)):
                if random.random() < AI.MUTATION_RATE:
                    child_chromosomes.append((f1[i]+f2[i])/2+0.5*np.random.randn())
                    continue
                child_chromosomes.append(f1[i] if i < split_at else f2[i])

            child_traits.append(np.array(child_chromosomes).reshape(t1.shape))

        return child_traits