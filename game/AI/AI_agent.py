import csv
import math

import numpy as np

from game.AI.AI_input_manager import AIInputManager
from game.AI.neural_network.neural_network import NeuralNetwork
from game.entities.car import Car


class AIAgent():
    def __init__(self, controlled_entity, neural_network):
        self.neural_network: NeuralNetwork = neural_network
        self.fitness_score = 0
        self.best_fitness = 0
        self.controlled_entity: Car = controlled_entity
        self.ai_input_manager = AIInputManager()

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

        self.inputs = []

    def get_genome(self):  # Genome is neural network weights and biases
        # return np.concatenate([param.data.numpy().flatten() for param in self.neural_network.get_parameters()])
        return self.neural_network.get_parameters()

    def evaluate_fitness(self):
        if self.controlled_entity.is_disabled():
            return self.last_fitness_score
        angle_to_next_checkpoint = abs(self.controlled_entity.car_knowledge.angle_to_next_checkpoint)
        angle_to_next_checkpoint = (angle_to_next_checkpoint - 0) / (180 - 0)  # Normalize angle between 0 and 1

        checkpoint_reward = self.evaluate_checkpoint_fitness()
        distance_penalty = self.evaluate_distance_to_checkpoint_fitness()
        speed_reward = self.evaluate_speed_fitness()
        regularization = 0.01 * np.random.normal()

        for neuron in self.inputs:
            if neuron == -2.0:
                self.fitness_score += 10
        self.fitness_score = (
                checkpoint_reward
                + distance_penalty
                - regularization
        )
        self.controlled_entity.set_fitness(self.fitness_score)
        if self.fitness_score > self.best_fitness:
            self.best_fitness = self.fitness_score

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
        average_speed = self.controlled_entity.car_knowledge.accumulator_speed / self.controlled_entity.car_knowledge.counter_frames
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
        penalty = self.distance_penalty * math.pow(distance / 160, 1.5)  # Penalización exponencial para distancias > 160
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

    def reset(self, car: Car):
        """
        Reset the agent attributes
        :param car: new car to control
        """
        self.fitness_distance_accumulated = 0
        self.fitness_score = float('-inf')
        self.best_fitness = float('-inf')
        self.controlled_entity = car
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
