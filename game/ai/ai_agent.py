import math

import numpy as np

from game.ai.ai_input_manager import AIInputManager
from game.ai.neural_network.neural_network import NeuralNetwork
from game.entities.car import Car


class AIAgent():
    def __init__(self, controlled_entity, neural_network):
        self.neural_network: NeuralNetwork = neural_network
        self.fitness_score = float('-inf')
        self.best_fitness = float('-inf')
        self.controlled_entity: Car = controlled_entity
        self.ai_input_manager = AIInputManager()

        self.fitness_score_log = ""

    def get_genome(self):  # Genome is neural network weights and biases
        # return np.concatenate([param.data.numpy().flatten() for param in self.neural_network.get_parameters()])
        return self.neural_network.get_parameters()

    def evaluate_fitness(self):
        # TODO: get the checkpoint number of the car
        checkpoint_reached = self.controlled_entity.car_knowledge.checkpoint_number
        # self.fitness_score = self.controlled_entity.checkpoint_number * 1000
        # # TODO: reward the agent for staying on track
        # tile_type_score = self.controlled_entity.car_knowledge.current_tile_type.value
        # self.fitness_score -= self.controlled_entity.current_tile_type.value
        # print(self.controlled_entity.current_tile_type)
        # TODO: get traveled distance
        # traveled_distance = self.controlled_entity.car_knowledge.traveled_distance
        # self.fitness_score += self.controlled_entity.traveled_distance
        # print(traveled_distance)
        # TODO: reward the agent for going forward

        # TODO: get the distance to the next checkpoint
        distance_to_next_checkpoint = self.controlled_entity.car_knowledge.distance_to_next_checkpoint
        # print(self.controlled_entity.distance_to_next_checkpoint)
        # TODO: reward the agent for going fast
        # TODO: penalize the agent for going off track
        # TODO: reward the agent for not crashing
        # TODO: reward the agent for not going backwards
        # TODO: reward the agent for not running over pedestrians
        # TODO: penalize the agent for not taking turns correctly
        # angle_difference = self.controlled_entity.angle_to_next_checkpoint - self.controlled_entity.car_entity.get_transform().get_rotation()
        angle_difference = self.calculate_angle_difference()

        # TODO: penalize time spent on sidewalk
        time_spent_on_sidewalk = self.controlled_entity.car_knowledge.chronometer_sidewalk.get_elapsed_time()
        # TODO: penalize time spent on grass
        time_spent_on_grass = self.controlled_entity.car_knowledge.chronometer_grass.get_elapsed_time()
        # TODO: reward time spent on track
        time_spent_on_track = self.controlled_entity.car_knowledge.chronometer_track.get_elapsed_time()
        # TODO: calculate average speed
        average_speed = self.controlled_entity.car_knowledge.accumulator_speed / self.controlled_entity.car_knowledge.counter_frames
        average_speed = (average_speed - (-200)) / (500 - (-200))
        # TODO: penalize time spent still
        time_staying_still = self.controlled_entity.car_knowledge.chronometer_still.get_elapsed_time()
        # velocidad media que ha tenido el coche, velocidad maxima
        # por debajo de velocidad maxima, mas reduces fitness sobre velocidad
        # penalizas por reducir velocidad maxima
        # quita mas entrar en cesped que reducir velocidad
        # penalizacion por atropellar peaton mayor que anteriores
        # quita mas punts estar en la acera que en el cesped

        # self.fitness_score = checkpoint_reached * 16 * 10 + 16 * 10 - distance_to_next_checkpoint - (
        #         angle_difference * angle_penalty) - time_spent_on_sidewalk * 25 - time_spent_on_grass * 50
        checkpoint_reward = (16 * 10) * checkpoint_reached
        distance_penalty = - 0.05 * distance_to_next_checkpoint
        angle_penalty = - (0.1 if angle_difference > 30 else 0) * angle_difference
        sidewalk_penalty = - 20 * time_spent_on_sidewalk
        still_penalty = - 30 * time_staying_still
        grass_penalty = - 100 * time_spent_on_grass
        track_reward = 0  # 30 * time_spent_on_track
        speed_reward = 100 * average_speed
        regularization = 0.01 * np.random.normal()

        self.fitness_score = (
                checkpoint_reward
                + distance_penalty + angle_penalty +
                + sidewalk_penalty
                + grass_penalty
                + track_reward
                + speed_reward
                + still_penalty
                - regularization
        )
        self.fitness_score_log = "" \
                                 "checkpoint_reward: {}\n" \
                                 "distance_penalty: {}\n" \
                                 "angle_penalty: {}\n" \
                                 "sidewalk_penalty: {}\n" \
                                 "still_penalty: {}\n" \
                                 "grass_penalty: {}\n" \
                                 "track_reward: {}\n" \
                                 "speed_reward: {}\n" \
                                 "regularization: {}\n" \
                                 "fitness_score: {}\n".format(checkpoint_reward, distance_penalty, angle_penalty,
                                                              sidewalk_penalty, still_penalty, grass_penalty,
                                                              track_reward, speed_reward, regularization,
                                                              self.fitness_score)
        # with open('fitness_score_log.txt', 'w') as f:
        #     f.write(f'checkpoint_reward: {checkpoint_reward}\n')
        #     f.write(f'distance_penalty: {distance_penalty}\n')
        #     f.write(f'angle_penalty: {angle_penalty}\n')
        #     f.write(f'sidewalk_penalty: {sidewalk_penalty}\n')
        #     f.write(f'still_penalty: {still_penalty}\n')
        #     f.write(f'grass_penalty: {grass_penalty}\n')
        #     f.write(f'track_reward: {track_reward}\n')
        #     f.write(f'speed_reward: {speed_reward}\n')
        #     f.write(f'regularization: {regularization}\n')
        #     f.write(f'fitness_score: {self.fitness_score}\n')

        self.controlled_entity.car_entity.set_fitness(self.fitness_score)
        if self.fitness_score > self.best_fitness:
            self.best_fitness = self.fitness_score

    def calculate_angle_difference(self):
        angle_threshold = 30  # Umbral de ángulo para considerar un giro correcto
        forward = self.controlled_entity.car_entity.get_transform().get_forward()
        entity_direction = math.degrees(math.atan2(forward.y, forward.x))

        angle_to_checkpoint = self.controlled_entity.car_knowledge.angle_to_next_checkpoint
        angle_difference = abs(angle_to_checkpoint - entity_direction)
        # if angle_difference < angle_threshold:
        #     return angle_difference
        return angle_difference

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
        self.controlled_entity = car
        self.fitness_score = 0
        self.controlled_entity.selected_as_parent = False
        self.controlled_entity.traveled_distance = 0
        self.controlled_entity.checkpoint_number = -1
        self.controlled_entity.current_tile_type = None
        self.controlled_entity.distance_to_next_checkpoint = 10 * 16

    def save_fitness_score_log(self):
        with open('fitness_score_log.txt', 'w') as f:
            f.write(self.fitness_score_log)
