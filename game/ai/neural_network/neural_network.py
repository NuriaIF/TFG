import numpy as np


class NeuralNetwork:
    def __init__(self, layer_sizes):
        """
        Initialize the neural network with a list of layers.

        :param layers: A list containing the number of nodes in each layer (including input and output)
        """
        self.layer_sizes = layer_sizes
        self.weights = []
        self.biases = []
        self.activations = []
        self.learning_rate = 0.01
        # self.weights = [np.random.randn(y, x) for x, y in zip(layers[:-1], layers[1:])]
        # self.biases = [np.random.randn(y, 1) for y in layers[1:]]
        self.init_weights_and_biases()

    def init_weights_and_biases(self):
        """
        Initialize weights and
        :return:
        """
        for x, y in zip(self.layer_sizes[:-1], self.layer_sizes[1:]):
            self.weights.append(np.random.randn(y, x))
            self.biases.append(np.random.randn(y, 1))

    def relu(self, z):
        """
        Apply the ReLU activation function.

        :param z: The input matrix
        :return: The activated output
        """
        return np.maximum(0, z)

    def softmax(self, x):
        """
        Apply the softmax activation function.

        :param x:
        :return:
        """
        exp_x = np.exp(x - np.max(x))
        return exp_x / exp_x.sum(axis=0)


    def forward(self, input_data):
        """
        Perform a forward pass and return the output of the network.

        :param input_data: The input data for the network
        :return: The output of the network's final layer
        """
        # input_data is a flat array and needs to be reshaped to a column vector
        # input_data = self.normalize_inputs(input_data)
        input_data = np.array(input_data, ndmin=2).T
        activations, _ = self._forward_propagation(input_data)
        final_output = activations[-1]
        return final_output.flatten()

    def _forward_propagation(self, input_data):
        """
        Perform forward propagation through the network, applying ReLU to hidden layers
        and Softmax to the output layer.

        :param input_data: The input data for the network
        :return: A tuple containing the list of activations and the list of z vectors for each layer
        """
        activation = input_data
        activations = [input_data]  # List to store all the activations, layer by layer
        zs = []  # List to store all the z vectors, layer by layer (input values of the activarion funcrion)

        for w, b in zip(self.weights[:-1], self.biases[:-1]):
            z = np.dot(w, activation) + b
            zs.append(z)
            activation = self.relu(z)
            activations.append(activation)

        z = np.dot(self.weights[-1], activation) + self.biases[-1]
        zs.append(z)
        activation = self.softmax(z)
        activations.append(activation)

        return activations, zs

    def get_parameters(self):
        # Este método extrae todos los parámetros de la red
        parametros = []
        for capa in self.capas:
            parametros.extend([capa.pesos.flatten(), capa.sesbos.flatten()])
        return np.concatenate(parametros)