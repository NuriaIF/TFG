"""
This module contains unit tests for the genetic algorithm
"""
import unittest
from unittest.mock import MagicMock

import numpy as np

from src.engine.ai.ai_agent import AIAgent
from src.engine.ai.genetic_algorithm.genetic_algorithm import GeneticAlgorithm


class TestGeneticAlgorithm(unittest.TestCase):
    def setUp(self):
        """
        This method will run before each test
        """
        self.ga = GeneticAlgorithm()
        # Create mock agents and configure them
        self.mock_agents = [MagicMock(spec=AIAgent), MagicMock(spec=AIAgent)]
        for i, agent in enumerate(self.mock_agents):
            agent.neural_network = MagicMock()
            agent.fitness_score = i  # Setting fitness scores 0, 1

    def test_load_and_get_agents(self):
        self.ga.load_agents(self.mock_agents)
        self.assertEqual(self.ga.get_agents(), self.mock_agents)

    def test_crossover(self):
        genome1 = np.array([])
        for i in range(100):
            genome1 = np.append(genome1, i)
        genome2 = np.array([])
        for i in range(100):
            genome2 = np.append(genome2, np.random.rand(1))

        child1, child2 = self.ga._crossover(genome1, genome2)

        for child in [child1, child2]:
            self.assertTrue(np.all(np.isin(child, genome1) | np.isin(child, genome2)))
            self.assertFalse(np.array_equal(child, genome1))
            self.assertFalse(np.array_equal(child, genome2))
            self.assertFalse(np.array_equal(child1, child2))

    def test_mutate(self):
        genome = np.array([])
        for i in range(100):
            genome = np.append(genome, i)
        original_genome = genome.copy()
        mutated = self.ga._mutate(genome)

        self.assertFalse(np.array_equal(original_genome, mutated),
                         "Genomes should not be identical after mutation")

    def test_evolve_agents(self):
        self.ga.load_agents(self.mock_agents)
        next_gen = self.ga.evolve_agents()

        self.assertEqual(len(next_gen), len(self.mock_agents))
        self.assertTrue(all(genome is not None for genome in next_gen))
        # Checking that top fitness is set correctly (mock agents have fitness scores 0 and 1)
        self.assertEqual(self.ga.top_fitness, 1)


if __name__ == '__main__':
    unittest.main()
