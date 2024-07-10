"""
This module contains the abstract class for AI agents
"""

from abc import abstractmethod, ABC
from src.engine.ai.neural_network.neural_network import NeuralNetwork


class AIAgent(ABC):
    """
    Abstract class for AI agents
    """

    def __init__(self, controlled_entity, neural_network):
        self.neural_network: NeuralNetwork = neural_network
        self.controlled_entity = controlled_entity
        self.fitness_score = 0

    def get_genome(self):  # Genome is neural network weights and biases
        """
        Get the genome of the agent (neural network weights and biases)
        :return: The genome of the agent
        """
        return self.neural_network.get_parameters()

    @abstractmethod
    def evaluate_fitness(self):
        """
        Evaluate the fitness of the agent
        """
        pass

    def reset(self, controlled_entity):
        """
        Reset the agent attributes
        """
        self.fitness_score = 0
        self.controlled_entity = controlled_entity
