import numpy as np


class Layer:
    def __init__(self, num_inputs, num_outputs, activation_function):
        # Inicialización de He para pesos
        self.weights = np.random.randn(num_outputs, num_inputs) * np.sqrt(2 / num_inputs)
        # Inicializar biases a cero
        self.biases = np.zeros((num_outputs, 1))
        self.activation_function = activation_function
        self.outputs = None

    def forward(self, inputs):
        z = np.dot(self.weights, inputs) + self.biases
        self.outputs = self.activation_function(z)
