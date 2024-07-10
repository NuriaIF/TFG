"""
This module contains unit tests for the neural network module
"""
import unittest
import numpy as np
from unittest.mock import patch
from src.engine.ai.neural_network.layer import Layer
from src.engine.ai.neural_network.neural_network import NeuralNetwork


class TestNeuralNetwork(unittest.TestCase):

    def setUp(self):
        """
        This method will run before each test
        """
        np.random.seed(42)  # Set seed for reproducibility
        self.nn = NeuralNetwork([3, 5, 2])

    def test_initialization(self):
        # Check if layers are initialized correctly
        self.assertEqual(len(self.nn.layers), 2)
        self.assertIsInstance(self.nn.layers[0], Layer)
        self.assertIsInstance(self.nn.layers[1], Layer)

    def test_forward(self):
        # Test forward pass
        input_data = [1, 2, 3]
        output = self.nn.forward(input_data)
        self.assertEqual(len(output), 2)  # Neural network has 2 output neurons

    def test_get_parameters(self):
        # Test getting parameters
        params = self.nn.get_parameters().copy()
        self.assertEqual(len(params), self.nn.get_total_params())
        self.assertTrue(np.array_equal(params, self.nn.get_parameters()))

    def test_set_parameters(self):
        # Test setting parameters
        params = np.random.rand(self.nn.get_total_params())
        self.nn.set_parameters(params)
        set_params = self.nn.get_parameters()
        np.testing.assert_array_equal(params, set_params)

    def test_save_load_parameters(self):
        # Test saving and loading parameters
        with patch('numpy.save') as mock_save, patch('numpy.load', return_value=np.random.rand(
                self.nn.get_total_params())) as mock_load:
            self.nn.save_parameters()
            mock_save.assert_called_once()
            self.nn.load_parameters()
            mock_load.assert_called_once()

    # def test_custom_activation(self):
    #     # Test custom activation function
    #     outputs = [0, 0, 0.6, 0.7]
    #     modified_outputs = self.nn.custom_activation(outputs)
    #     self.assertEqual(modified_outputs[2], 0)
    #     self.assertEqual(modified_outputs[3], 0)

    def test_relu(self):
        # Test ReLU function
        z = np.array([-1, 0, 1])
        activated = self.nn.relu(z)
        expected = np.array([0, 0, 1])
        np.testing.assert_array_equal(activated, expected)

    # def test_sigmoid(self):
    #     # Test sigmoid function
    #     z = np.array([0])
    #     activated = self.nn.sigmoid(z)
    #     expected = np.array([0.5])
    #     np.testing.assert_array_equal(activated, expected)
    #
    # def test_softmax(self):
    #     # Test softmax function
    #     x = np.array([1, 2, 3])
    #     activated = self.nn.softmax(x)
    #     expected = np.exp(x) / np.sum(np.exp(x))
    #     np.testing.assert_almost_equal(activated, expected)
    #
    # def test_leaky_relu(self):
    #     # Test leaky ReLU function
    #     z = np.array([-1, 0, 1])
    #     activated = self.nn.leaky_relu(z)
    #     expected = np.array([-0.01, 0, 1])
    #     np.testing.assert_array_equal(activated, expected)

    def test_layer_forward_pass(self):
        # Test that each layer computes forward pass correctly
        inputs = np.random.rand(self.nn.layer_sizes[0], 1)  # Random inputs appropriate for the input size
        current_input = inputs

        for layer in self.nn.layers:
            old_outputs = np.copy(layer.outputs)  # Make a copy of the old outputs before forward pass
            layer.forward(current_input)
            z = np.dot(layer.weights, current_input) + layer.biases
            expected_outputs = layer.activation_function(z)

            # Verify that outputs are computed correctly
            np.testing.assert_array_almost_equal(layer.outputs, expected_outputs)

            # Set up input for next layer
            current_input = layer.outputs

            # Ensure outputs change after forward pass, compare arrays properly
            if old_outputs is not None:
                self.assertFalse(np.array_equal(old_outputs, layer.outputs))

    def test_initial_layer_weights_biases(self):
        # Test weights and biases initialization in each layer
        for i, layer in enumerate(self.nn.layers):
            # Weights should be initialized with 'He' initialization formula
            self.assertEqual(layer.weights.shape, (layer.biases.size, self.nn.layer_sizes[i]))
            self.assertTrue(np.all(layer.biases == 0))  # Biases should be initialized to zero

            # Check if the standard deviation of weights is within a reasonable range
            expected_std = np.sqrt(2 / self.nn.layer_sizes[i])
            std_deviation = np.std(layer.weights)
            # Set a tolerance percentage (e.g., 20% of the expected standard deviation)
            tolerance = 0.2 * expected_std
            self.assertTrue(abs(std_deviation - expected_std) <= tolerance,
                            f"Expected std deviation around {expected_std}, but got {std_deviation}")

    def test_negative_number_of_neurons(self):
        # Test initialization with a negative number of neurons in the input layer
        with self.assertRaises(ValueError):
            NeuralNetwork([-3, 5, 2])

        # Test initialization with a negative number of neurons in the hidden layer
        with self.assertRaises(ValueError):
            NeuralNetwork([3, 5, -2])

        # Test initialization with a negative number of neurons in the output layer
        with self.assertRaises(ValueError):
            NeuralNetwork([3, 5, -2])

        # Test initialization with a negative number of neurons in all layers
        with self.assertRaises(ValueError):
            NeuralNetwork([-3, -5, -2])


if __name__ == '__main__':
    unittest.main()
