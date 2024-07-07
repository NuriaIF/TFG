import math

import numpy as np

from src.engine.ai.ai_agent import AIAgent
from src.engine.ai.neural_network.neural_network import NeuralNetwork
from src.game.entities.car import Car


class CarAIAgent(AIAgent):
    def __init__(self, controlled_entity: Car, neural_network: NeuralNetwork):
        super().__init__(controlled_entity, neural_network)
        self.fitness_score_log = ""
        self.checkpoint_reward = 80
        self.distance_penalty = - 0.5
        self.angle_penalty = - 100
        self.sidewalk_penalty = - 40
        self.still_penalty = - 80
        self.grass_penalty = - 30
        self.track_reward = 0  # 30 * time_spent_on_track
        self.speed_reward = 100
        self.collisions_penalty = - 10

        self.fitness_distance_accumulated = 0

        self.fitness_score_by_checkpoint = 0
        self.fitness_score_by_distance = 0
        self.fitness_score_by_speed = 0

        self.last_fitness_score = 0
        self.last_fitness_score_by_checkpoint = 0
        self.last_fitness_score_by_distance = 0
        self.last_fitness_score_by_speed = 0

    def get_genome(self):  # Genome is neural network weights and biases
        # return np.concatenate([param.data.numpy().flatten() for param in self.neural_network.get_parameters()])
        return self.neural_network.get_parameters()

    def evaluate_fitness(self):
        if self.controlled_entity.is_disabled():
            return self.last_fitness_score

        checkpoint_reward = self.evaluate_checkpoint_fitness()
        distance_penalty = self.evaluate_distance_to_checkpoint_fitness()
        regularization = 0.01 * np.random.normal()

        self.fitness_score = (
                checkpoint_reward
                + distance_penalty
                - regularization
        )
        self.controlled_entity.set_fitness(self.fitness_score)

        self.fitness_score = self.controlled_entity.car_knowledge.traveled_distance
        self.last_fitness_score = self.fitness_score
        return self.fitness_score

    def evaluate_checkpoint_fitness(self):
        if self.controlled_entity.is_disabled():
            return self.last_fitness_score_by_checkpoint
        checkpoint_reached = self.controlled_entity.car_knowledge.checkpoint_value

        checkpoint_reward = self.checkpoint_reward * checkpoint_reached
        self.fitness_score_by_checkpoint = checkpoint_reward

        self.last_fitness_score_by_checkpoint = self.fitness_score_by_checkpoint
        return self.fitness_score_by_checkpoint

    def evaluate_speed_fitness(self):
        if self.controlled_entity.car_knowledge.counter_frames == 0:
            return 0
        if self.controlled_entity.is_disabled():
            return self.last_fitness_score_by_speed
        average_speed = (self.controlled_entity.car_knowledge.accumulator_speed /
                         self.controlled_entity.car_knowledge.counter_frames)
        average_speed = (average_speed - (-200)) / (500 - (-200))
        # penalize time spent still
        time_staying_still = self.controlled_entity.car_knowledge.chronometer_still.get_elapsed_time()

        still_penalty = self.still_penalty * time_staying_still
        speed_reward = self.speed_reward * average_speed

        self.fitness_score_by_speed = still_penalty + speed_reward
        self.last_fitness_score_by_speed = self.fitness_score_by_speed
        return self.fitness_score_by_speed

    def evaluate_distance_to_checkpoint_fitness(self):
        if self.controlled_entity.is_disabled():
            return self.last_fitness_score_by_distance
        distance = self.controlled_entity.car_knowledge.distance_to_next_checkpoint
        penalty = self.distance_penalty * math.pow(distance / 160, 1.5)
        self.fitness_distance_accumulated += penalty
        self.fitness_score_by_distance = self.fitness_distance_accumulated
        self.last_fitness_score_by_distance = self.fitness_score_by_distance
        return self.fitness_score_by_distance

    def select_as_parent(self):
        """
        Select the agent as parent
        """
        self.controlled_entity.selected_as_parent = True

    def deselect_as_parent(self):
        """
        Deselect the agent as parent
        """
        self.controlled_entity.selected_as_parent = False

    def reset(self, controlled_entity):
        """
        Reset the agent attributes
        :param controlled_entity: entity controlled by the agent
        """
        super().reset(controlled_entity)
        self.fitness_distance_accumulated = 0
        self.controlled_entity.selected_as_parent = False
        self.controlled_entity.traveled_distance = 0
        self.controlled_entity.checkpoint_number = -1
        self.controlled_entity.checkpoint_value = -1
        self.controlled_entity.lap_number = 0
        self.controlled_entity.current_tile_type = None
        self.controlled_entity.distance_to_next_checkpoint = 10 * 16

    def save_fitness_score_log(self):
        with open('fitness_score_log.txt', 'w') as f:
            f.write(self.fitness_score_log)
