import numpy as np

from game.ai.neural_network.layer import Layer


class NeuralNetwork:
    def __init__(self, layer_sizes: list[int]):
        """
        Initialize the neural network with a list of layers.

        :param layers: A list containing the number of nodes in each layer (including input and output)
        """
        self.layer_sizes = layer_sizes
        self.layers: list[Layer] = []
        # Relu activation function for hidden layers and softmax for output layer
        # print(layer_sizes)
        for i in range(len(layer_sizes) - 2):
            self.layers.append(Layer(layer_sizes[i], layer_sizes[i + 1], self.relu))
        self.layers.append(Layer(layer_sizes[-2], layer_sizes[-1], self.softmax))

        self.learning_rate = 0.01

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
