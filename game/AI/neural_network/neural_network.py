import numpy as np

from game.AI.neural_network.layer import Layer


class NeuralNetwork:
    def __init__(self, layer_sizes: list[int], parameters=None):
        """
        Initialize the neural network with a list of layers.

        :param layers: A list containing the number of nodes in each layer (including input and output)
        """
        self.layer_sizes: list[int] = layer_sizes
        self.layers: list[Layer] = []
        for i in range(len(layer_sizes) - 1):
            activation_func = self.relu if i < len(layer_sizes) - 2 else self.leaky_relu
            self.layers.append(Layer(layer_sizes[i], layer_sizes[i + 1], activation_func))
        self.learning_rate: float = 0.01
        if parameters is not None:
            self.set_parameters(parameters)

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
        # exp_x = np.exp(x - np.max(x))
        # return exp_x / exp_x.sum(axis=0)
        scale = np.max(x) / 2  # Escala basada en el valor máximo para reducir la gama de valores
        exp_x = np.exp((x - np.max(x)) / scale)
        return exp_x / np.sum(exp_x, axis=0, keepdims=True)

    # def leaky_relu(self, z):
    #     """
    #     Apply the Leaky ReLU activation function.
    #     :param z: 
    #     :return: 
    #     """
    #     return np.maximum(0.01 * z, z)
    def leaky_relu(self, z, alpha=0.01):
        return np.where(z > 0, z, z * alpha)

    def forward(self, input_data):
        """
        Perform a forward pass and return the output of the network.

        :param input_data: The input data for the network
        :return: The output of the network's final layer
        """
        # input_data is a flat array and needs to be reshaped to a column vector
        input_data = np.array(input_data, ndmin=2).T
        for layer in self.layers:
            layer.forward(input_data)
            input_data = layer.outputs
        output = input_data
        return output.flatten()

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
            raise ValueError(f"Length of parameters {len(parameters)} does not match expected length {expected_length}.")

        start = 0
        for layer in self.layers:
            end = start + layer.weights.size
            layer.weights = parameters[start:end].reshape(layer.weights.shape)
            start = end

            end = start + layer.biases.size
            layer.biases = parameters[start:end].reshape(layer.biases.shape)
            start = end

    def get_parameters(self):
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
        np.save("parameters.npy", self.get_parameters())

    def load_parameters(self):
        """
        Load the parameters of the neural network from a file.
        :return: 
        """
        # Load the parameters of the neural network from a file
        self.set_parameters(np.load("parameters.npy"))

    def get_total_params(self):
        """
        Get the total number of parameters in the network.
        :return: The total number of parameters in the network
        """
        return sum(layer.weights.size + layer.biases.size for layer in self.layers)
