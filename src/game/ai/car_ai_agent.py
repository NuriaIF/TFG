"""
Car AI agent module that contains the CarAIAgent class.
"""
import numpy as np

from src.engine.ai.ai_agent import AIAgent
from src.engine.ai.neural_network.neural_network import NeuralNetwork
from src.game.entities.car import Car


class CarAIAgent(AIAgent):
    """
    Car AI agent class that represents a car AI agent in the game.
    """
    def __init__(self, controlled_entity: Car, neural_network: NeuralNetwork):
        super().__init__(controlled_entity, neural_network)
        self.fitness_score_log: str = ""
        self.last_fitness_score: float = 0

    def get_genome(self):  # Genome is neural network weights and biases
        return self.neural_network.get_parameters()

    def evaluate_fitness(self):
        if self.controlled_entity.is_disabled():
            return self.last_fitness_score

        self.fitness_score = self.controlled_entity.car_knowledge.traveled_distance
        self.last_fitness_score = self.fitness_score
        return self.fitness_score

    def reset(self, controlled_entity):
        """
        Reset the agent attributes
        :param controlled_entity: entity controlled by the agent
        """
        super().reset(controlled_entity)
        self.controlled_entity.traveled_distance = 0
        self.controlled_entity.checkpoint_number = -1
        self.controlled_entity.checkpoint_value = -1
        self.controlled_entity.lap_number = 0
        self.controlled_entity.current_tile_type = None
        self.controlled_entity.distance_to_next_checkpoint = 10 * 16

    def save_fitness_score_log(self):
        """
        Save the fitness score log to a file
        """
        with open('fitness_score_log.txt', 'w') as f:
            f.write(self.fitness_score_log)
