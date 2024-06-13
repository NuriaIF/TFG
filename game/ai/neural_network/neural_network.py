import numpy as np

from game.ai.neural_network.layer import Layer


class NeuralNetwork:
    def __init__(self, layer_sizes: list[int]):
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


    # def _forward_propagation(self, input_data):
    #     """
    #     Perform forward propagation through the network, applying ReLU to hidden layers
    #     and Softmax to the output layer.
    # 
    #     :param input_data: The input data for the network
    #     :return: A tuple containing the list of activations and the list of z vectors for each layer
    #     """
    #     activation = input_data
    #     activations = [input_data]  # List to store all the activations, layer by layer
    #     zs = []  # List to store all the z vectors, layer by layer (input values of the activation function)
    # 
    #     for w, b in zip(self.weights[:-1], self.biases[:-1]):
    #         z = np.dot(w, activation) + b
    #         zs.append(z)
    #         activation = self.relu(z)
    #         activations.append(activation)
    # 
    #     z = np.dot(self.weights[-1], activation) + self.biases[-1]
    #     zs.append(z)
    #     activation = self.softmax(z)
    #     activations.append(activation)
    # 
    #     return activations, zs

    def set_parameters(self, parameters):
        """
        Set the genome of the agent.

        :param parameters: The genome of the agent
        """
        # This method is used to set the genome of the agent

        expected_length = sum(layer.weights.size + layer.biases.size for layer in self.layers)

        if len(parameters) != expected_length:
            raise ValueError(
                f"Length of parameters {len(parameters)} does not match expected length {expected_length}.")

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
        # This method is used to get the genome of the agent
        parameters = []
        for layer in self.layers:
            parameters.extend([layer.weights.flatten(), layer.biases.flatten()])
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
        self.set_parameters(np.load("best.npy"))

    def get_total_params(self):
        """
        Get the total number of parameters in the network.
        :return: The total number of parameters in the network
        """
        return sum(layer.weights.size + layer.biases.size for layer in self.layers)
