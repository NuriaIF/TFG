import numpy as np


class Layer:
    def __init__(self, num_inputs, num_outputs, activation_function):
        self.weights = np.random.rand(num_outputs, num_inputs) - 0.5
        self.biases = np.random.rand(num_outputs, 1) - 0.5
        self.activation_function = activation_function
        self.outputs = None

    def forward(self, inputs):
        z = np.dot(self.weights, inputs) + self.biases
        self.outputs = self.activation_function(z)
