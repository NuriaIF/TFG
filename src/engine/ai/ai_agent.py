from abc import abstractmethod, ABC

from src.engine.ai.neural_network.neural_network import NeuralNetwork


class AIAgent(ABC):
    def __init__(self, controlled_entity, neural_network):
        self.neural_network: NeuralNetwork = neural_network
        self.controlled_entity = controlled_entity
        self.fitness_score = 0

    def get_genome(self):  # Genome is neural network weights and biases
        return self.neural_network.get_parameters()

    @abstractmethod
    def evaluate_fitness(self):
        pass

    def reset(self, controlled_entity):
        """
        Reset the agent attributes
        """
        self.fitness_score = 0
        self.controlled_entity = controlled_entity

