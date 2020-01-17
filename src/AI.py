import random

import numpy as np

ACTIVATION_SIGMOID = lambda x: 1.0 / (1.0 + np.exp(-x))


class AI:
    MUTATION_RATE = 0.1

    def __init__(self, dimensions, weights=None):
        self.n_layers = len(dimensions)
        self.dimensions = dimensions
        self.weights = weights

        # the weights are matrices with dimensions of n_neurons(l) x n_neurons(l+1)
        # we index backwards (j, k) to optimize for matrix transformation
        if not weights:
            self.weights = [np.random.randn(j, k) for k, j in zip(dimensions[:-1], dimensions[1:])]

    def feedforward_la(self, activation):
        for w in self.weights:
            activation = np.dot(w, activation)  # a = f(w . a + b)
        return activation

    @staticmethod
    def cross_over(mate1, mate2):
        child_weights = []
        for w1, w2 in zip(mate1.weights, mate2.weights):
            f1 = w1.flatten()
            f2 = w2.flatten()
            child_chromosomes = []
            split_at = random.randint(0, len(f1))

            for i in range(len(f1)):
                # if random.random() < AI.MUTATION_RATE:
                #     child_chromosomes.append(np.random.randn())
                #     continue

                child_chromosomes.append(f1[i] if i < split_at else f2[i])

            child_weights.append(np.array(child_chromosomes).reshape(w1.shape))
        return AI(mate1.dimensions, child_weights)
