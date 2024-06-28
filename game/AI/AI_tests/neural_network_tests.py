import unittest
import numpy as np

from game.AI.neural_network.neural_network import NeuralNetwork


class TestNeuralNetwork(unittest.TestCase):

    def setUp(self):
        self.nn = NeuralNetwork(layer_sizes=[2, 3, 2])

    def test_initialization(self):
        # Verify that the neural network is initialized correctly
        self.assertEqual(len(self.nn.layers), 2)
        self.assertEqual(self.nn.layers[0].weights.shape, (3, 2))
        self.assertEqual(self.nn.layers[1].weights.shape, (2, 3))

    def test_forward_pass(self):
        # Verify that the forward pass returns the expected number of outputs
        input_data = [0.5, -0.5]
        output = self.nn.forward(input_data)
        self.assertEqual(len(output), 2)  # Must be the same as the number of neurons in the output layer

    def test_set_and_get_parameters(self):
        # Verify get parameters and set parameters consistency
        params = np.random.rand(self.nn.get_total_params())
        self.nn.set_parameters(params)
        retrieved_params = self.nn.get_parameters()
        np.testing.assert_array_almost_equal(params, retrieved_params)

    def test_correct_parameters(self):
        # Set random parameters
        params = np.random.rand(self.nn.get_total_params())
        self.nn.set_parameters(params)
        # TODO: añadir verificaciones para asegurarte de que los parámetros se han establecido correctamente

    def test_incorrect_parameters_length(self):
        params = np.random.rand(self.nn.get_total_params() + 1)  # Incorrect length
        with self.assertRaises(ValueError):
            self.nn.set_parameters(params)

    def test_output_functions(self):
        self.assertTrue(np.all(self.nn.relu(np.array([-1, 0, 1])) == np.array([0, 0, 1])))
        self.assertTrue(np.all(self.nn.leaky_relu(np.array([-1, 0, 1])) == np.array([-0.01, 0, 1])))

    def test_activation_consistency(self):
        input_data = np.array([0.5, -0.5])
        self.nn.set_parameters(np.random.rand(self.nn.get_total_params()))  # Establecer parámetros aleatorios
        first_run = self.nn.forward(input_data)
        second_run = self.nn.forward(input_data)
        np.testing.assert_array_almost_equal(first_run, second_run)

    def test_network_scalability(self):
        large_nn = NeuralNetwork(layer_sizes=[10, 100, 10])
        input_data = np.random.rand(10)
        output = large_nn.forward(input_data)
        self.assertEqual(len(output), 10)

    def test_relu(self):
        input_values = np.array([-2, -1, 0, 1, 2])
        expected_output = np.array([0, 0, 0, 1, 2])
        relu_output = self.nn.relu(input_values)
        np.testing.assert_array_equal(relu_output, expected_output)

    def test_leaky_relu(self):
        input_values = np.array([-2, -1, 0, 1, 2])
        expected_output = np.array([-0.02, -0.01, 0, 1, 2])  # Considerando un slope de 0.01
        leaky_relu_output = self.nn.leaky_relu(input_values)
        np.testing.assert_array_almost_equal(leaky_relu_output, expected_output, decimal=2)

    # def test_softmax_stability(self):
    #     # Verificar que softmax maneja correctamente entradas grandes
    #     large_input = np.array([1000, 1001, 1002])
    #     output = self.nn.softmax(large_input)
    #     expected_output = np.array(
    #         [0, 0, 1])  # Debido a la precisión de punto flotante, el último debería ser el más grande
    #     self.assertTrue(np.allclose(output, expected_output, atol=1e-5))
    # 
    # def test_softmax_stability(self):
    #     large_input = np.array([1000, 1001, 1002])
    #     print("Input:", large_input)
    #     output = self.nn.softmax(large_input)
    #     print("Output:", output)
    #     expected_output = np.array([0, 0, 1])
    #     self.assertTrue(np.allclose(output, expected_output, atol=1e-3))


if __name__ == '__main__':
    unittest.main()
