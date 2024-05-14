import unittest
import numpy as np
from unittest.mock import MagicMock

from game.ai.genetic_algorithm.genetic_algorithm import GeneticAlgorithm
from game.ai.ai_agent import AIAgent

class TestGeneticAlgorithm(unittest.TestCase):
    def setUp(self):
        # Configure the selection callback mock, don't need to do anything
        self.selection_callback = MagicMock()

        # Create the genetic algorithm instance
        self.ga = GeneticAlgorithm(self.selection_callback)

        # Create a list of mock agents to be used in the tests
        self.mock_agents = [MagicMock(spec=AIAgent) for _ in range(10)]
        for agent in self.mock_agents:
            agent.get_genome.return_value = np.random.rand(10)  # Random genomes of length 10
            agent.fitness_score = np.random.rand()
            mock_neural_network = MagicMock()
            agent.neural_network = mock_neural_network
            mock_car = MagicMock()
            agent.controlled_entity = mock_car

        self.ga._agents = self.mock_agents  # Add the mock agents to the genetic algorithm

    def test_evolve_agents(self):
        print(self.ga.get_agents())
        self.assertNotEqual(len(self.ga.get_agents()), 0, "There should be agents to evolve")

        original_count = len(self.ga.get_agents())
        self.ga.evolve_agents()
        self.assertEqual(len(self.ga.get_agents()), original_count,
                         "The number of agents should remain the same after evolving")
        self.selection_callback.assert_called_once()  # Verify that the selection callback was called

    def test_crossover(self):
        # Test that the crossover operation produces a valid genome
        parent1_genome = np.array([1, 2, 3, 4, 5])
        parent2_genome = np.array([5, 4, 3, 2, 1])
        child_genome = self.ga._crossover(parent1_genome, parent2_genome)
        self.assertEqual(len(child_genome), len(parent1_genome))  # Genome length should be the same

    def test_mutate(self):
        genome = np.zeros(100)
        original_genome = genome.copy()
        mutated = False

        for _ in range(100):  # Try to mutate the genome 100 times, to increase the chances of mutation
            mutated_genome = self.ga._mutate(genome.copy())
            if not np.array_equal(original_genome, mutated_genome):
                mutated = True
                break

        self.assertTrue(mutated, "The genome should have mutated at least once")

    def test_mutation_rate(self):
        # Test that the mutation rate is being applied correctly
        genome = np.zeros(100)
        self.ga.mutation_rate = 1  # Set the mutation rate to 100%
        mutated_genome = self.ga._mutate(genome.copy())
        self.assertNotEqual(list(genome), list(mutated_genome))  # The genome should have changed in every position


if __name__ == '__main__':
    unittest.main()
