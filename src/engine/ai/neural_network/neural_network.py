"""
This module contains the NeuralNetwork class, which represents a neural network.
"""
import numpy as np

from src.engine.ai.neural_network.layer import Layer


class NeuralNetwork:
    """
    This class represents a neural network
    """
    def __init__(self, layer_sizes: list[int], parameters=None):
        """
        Initialize the neural network with the given layer sizes.
        :param layer_sizes: The sizes of the layers in the network
        """
        if any(n <= 0 for n in layer_sizes):
            raise ValueError("All layer sizes must be positive integers.")

        self.layer_sizes: list[int] = layer_sizes
        self.layers: list[Layer] = []
        for i in range(len(layer_sizes) - 1):
            activation_func = self.relu if i < len(layer_sizes) - 2 else self.sigmoid
            self.layers.append(Layer(layer_sizes[i], layer_sizes[i + 1], activation_func))
        self.learning_rate: float = 0.01
        if parameters is not None:
            self.set_parameters(parameters)

        self.inputs = []
        self.outputs = []

    @staticmethod
    def relu(z):
        """
        Apply the ReLU activation function.

        :param z: The input matrix
        :return: The activated output
        """
        return np.maximum(0, z)

    @staticmethod
    def sigmoid(z):
        """
        Apply the sigmoid activation function.

        :param z: The input matrix
        :return: The activated output
        """
        return 1 / (1 + np.exp(-z))

    @staticmethod
    def softmax(x):
        """
        Apply the softmax activation function.

        :param x:
        :return:
        """
        exp_x = np.exp(x - np.max(x))
        return exp_x / exp_x.sum(axis=0, keepdims=True)

    @staticmethod
    def leaky_relu(z, alpha=0.01):
        """
        Apply the Leaky ReLU activation function, with a default alpha value of 0.01.
        Return z if z > 0, otherwise return z * alpha.
        :param z:
        :param alpha:
        :return:
        """
        return np.where(z > 0, z, z * alpha)

    def forward(self, input_data):
        """
        Perform a forward pass and return the output of the network.

        :param input_data: The input data for the network
        :return: The output of the network's final layer
        """
        # input_data is a flat array and needs to be reshaped to a column vector
        self.inputs = input_data
        input_data = np.array(input_data, ndmin=2).T
        for layer in self.layers:
            layer.forward(input_data)
            input_data = layer.outputs

        output = input_data
        self.outputs = self.custom_activation(output.flatten())
        return self.outputs

    def get_activations(self, input_data):
        """
        Perform a forward pass and return the activations of all layers.

        :param input_data: The input data for the network
        :return: A list of activations for each layer
        """
        activations = [np.array(input_data, ndmin=2).T]  # Start with the input data as the first activation
        current_data = activations[0]
        for layer in self.layers:
            layer.forward(current_data)
            current_data = layer.outputs
            activations.append(current_data)
        return [a.flatten() for a in activations]

    def set_parameters(self, parameters):
        """
        Set the genome of the agent.
        :param parameters: The genome of the agent
        """
        expected_length = sum(layer.weights.size + layer.biases.size for layer in self.layers)

        if len(parameters) != expected_length:
            raise ValueError(f"Length of parameters {len(parameters)} does not match expected length {expected_length}")

        start = 0
        for layer in self.layers:
            end = start + layer.weights.size
            layer.weights = parameters[start:end].reshape(layer.weights.shape)
            start = end

            end = start + layer.biases.size
            layer.biases = parameters[start:end].reshape(layer.biases.shape)
            start = end

    def get_parameters(self) -> np.ndarray:
        """
        Get the genome of the agent.
        :return: The genome of the agent
        """
        parameters = []
        for layer in self.layers:
            parameters.append(layer.weights.flatten())
            parameters.append(layer.biases.flatten())
        return np.concatenate(parameters)

    def save_parameters(self):
        """
        Save the parameters of the neural network to a file.
        :return: 
        """
        # Save the parameters of the neural network to a file
        np.save("assets/data_files/models/road04_trained.npy", self.get_parameters())

    def load_parameters(self):
        """
        Load the parameters of the neural network from a file.
        :return: 
        """
        # Load the parameters of the neural network from a file
        self.set_parameters(np.load("assets/data_files/models/road03_trained.npy"))

    def get_total_params(self):
        """
        Get the total number of parameters in the network.
        :return: The total number of parameters in the network
        """
        return sum(layer.weights.size + layer.biases.size for layer in self.layers)

    @staticmethod
    def custom_activation(outputs):
        """
        Custom activation function for the network to ensure that the network outputs are valid.
        :param outputs: The outputs of the network
        :return: The modified outputs of the network
        """
        if len(outputs) < 4:
            return outputs
        if outputs[2] > 0.5 and outputs[3] > 0.5:
            outputs[2] = 0
            outputs[3] = 0
        return outputs
