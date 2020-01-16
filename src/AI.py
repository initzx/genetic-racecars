import numpy as np

ACTIVATION_SIGMOID = lambda x: 1.0 / (1.0 + np.exp(-x))


class AI:
    def __init__(self, dimensions, weights=None):
        self.n_layers = len(dimensions)
        self.dimensions = dimensions
        self.weights = weights
        self.activ_func = ACTIVATION_SIGMOID

        # the weights are matrices with dimensions of n_neurons(l) x n_neurons(l+1)
        # we index backwards (j, k) to optimize for matrix transformation
        if not weights:
            self.weights = [np.random.randn(j, k) for k, j in zip(dimensions[:-1], dimensions[1:])]

    def feedforward_la(self, activation):
        for w in self.weights:
            activation = self.activ_func(np.dot(w, activation))  # a = f(w . a + b)
        return activation
