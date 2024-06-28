import unittest

from matplotlib import pyplot as plt

from game.AI.neural_network.neural_network import NeuralNetwork


class TestPopulationDiversity(unittest.TestCase):

    def setUp(self):
        # create a list of neural networks
        self.nns = [NeuralNetwork(layer_sizes=[292, 150, 60, 6]) for _ in range(100)]
    def test_analyze_population_diversity(self):
        all_weights = []
        all_biases = []

        for neuralnet in self.nns:
            for layer in neuralnet.layers:
                all_weights.extend(layer.weights.flatten())
                all_biases.extend(layer.weights.flatten())

        self.assertEqual(len(all_weights), 100 * (292 * 150 + 150 * 60 + 60 * 6))

        plt.hist(all_weights, bins=100, alpha=0.5, label='Weights')
        plt.hist(all_biases, bins=100, alpha=0.5, label='Biases')
        plt.legend(loc='upper right')
        plt.title('Distribución de Pesos y Biases Iniciales')
        plt.show()


if __name__ == '__main__':
    unittest.main()
