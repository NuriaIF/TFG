"""
This file contains the Layer class, which represents a single layer in a neural network.
"""
import numpy as np


class Layer:
    """
    This class represents a single layer in a neural network.
    """
    def __init__(self, num_inputs, num_outputs, activation_function):
        # 'He' initialization for weights
        self.weights = np.random.randn(num_outputs, num_inputs) * np.sqrt(2 / num_inputs)
        # Initialize biases to 0
        self.biases = np.zeros((num_outputs, 1))
        self.activation_function = activation_function
        self.outputs = None

    def forward(self, inputs):
        """
        Forward pass through the layer
        :param inputs:
        :return:
        """
        z = np.dot(self.weights, inputs) + self.biases
        self.outputs = self.activation_function(z)

