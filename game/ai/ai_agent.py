import math

import numpy as np

from game.ai.ai_input_manager import AIInputManager
from game.entities.car import Car


class AIAgent():
    def __init__(self, controlled_entity, neural_network):
        self.neural_network = neural_network
        self.fitness_score = 0
        self.controlled_entity: Car = controlled_entity
        self.ai_input_manager = AIInputManager()

    def get_genome(self):  # Genome is neural network weights and biases
        # return np.concatenate([param.data.numpy().flatten() for param in self.neural_network.get_parameters()])
        return self.neural_network.get_parameters()

    def evaluate_fitness(self):
        # TODO: get the checkpoint number of the car
        checkpoint_reached = self.controlled_entity.checkpoint_number
        # self.fitness_score = self.controlled_entity.checkpoint_number * 1000
        # TODO: reward the agent for staying on track
        tile_type_score = self.controlled_entity.current_tile_type.value
        # self.fitness_score -= self.controlled_entity.current_tile_type.value
        # print(self.controlled_entity.current_tile_type)
        # TODO: get traveled distance
        traveled_distance = self.controlled_entity.traveled_distance
        # self.fitness_score += self.controlled_entity.traveled_distance
        # print(traveled_distance)
        # TODO: reward the agent for going forward

        # TODO: get the distance to the next checkpoint
        distance_to_next_checkpoint = self.controlled_entity.distance_to_next_checkpoint
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
        time_spent_on_sidewalk = self.controlled_entity.is_on_sidewalk.count(True) / len(
            self.controlled_entity.is_on_sidewalk) if len(
            self.controlled_entity.is_on_sidewalk) > 0 else 0  # 0-1
        # TODO: penalize time spent on grass
        time_spent_on_grass = self.controlled_entity.is_on_grass.count(True) / len(
            self.controlled_entity.is_on_grass) if len(
            self.controlled_entity.is_on_grass) > 0 else 0  # 0-1
        # TODO: reward time spent on track
        time_spent_on_track = self.controlled_entity.is_on_track.count(True) / len(
            self.controlled_entity.is_on_track) if len(
            self.controlled_entity.is_on_track) > 0 else 0
        # TODO: calculate average speed
        average_speed = sum(self.controlled_entity.speeds) / len(self.controlled_entity.speeds) if len(
            self.controlled_entity.speeds) > 0 else 0
        # velocidad media que ha tenido el coche, velocidad maxima
        # por debajo de velocidad maxima, mas reduces fitness sobre velocidad
        # penalizas por reducir velocidad maxima
        # quita mas entrar en cesped que reducir velocidad
        # penalizacion por atropellar peaton mayor que anteriores
        # quita mas puntos estar en la acera que en el cesped

        # self.fitness_score = checkpoint_reached * 16 * 10 + 16 * 10 - distance_to_next_checkpoint - (
        #         angle_difference * angle_penalty) - time_spent_on_sidewalk * 25 - time_spent_on_grass * 50
        checkpoint_reward = 16 * 10
        distance_penalty = 1
        angle_penalty = 0.25 if angle_difference > 30 else 0
        sidewalk_penalty = 20
        grass_penalty = 40
        track_reward = 20
        speed_reward = 1
        regularization = 0.01 * np.random.normal()

        self.fitness_score = (
                checkpoint_reached * checkpoint_reward +
                checkpoint_reward -
                distance_to_next_checkpoint * distance_penalty -
                angle_difference * angle_penalty -
                time_spent_on_sidewalk * sidewalk_penalty -
                time_spent_on_grass * grass_penalty +
                time_spent_on_track * track_reward +
                average_speed * speed_reward +
                regularization
        )

        # save to file each partial fitness for debugging
        # with open("fitness.txt", "a") as f:
        #     f.write(f"Checkpoint: {checkpoint_reached * checkpoint_reward}\n")
        #     f.write(f"Distance to next checkpoint: {checkpoint_reward - distance_penalty}\n")
        #     f.write(f"Angle difference: {angle_difference * angle_penalty}\n")
        #     f.write(f"Time spent on sidewalk: {time_spent_on_sidewalk * sidewalk_penalty}\n")
        #     f.write(f"Time spent on grass: {time_spent_on_grass * grass_penalty}\n")
        #     f.write(f"Total fitness: {self.fitness_score}\n")

        self.controlled_entity.car_entity.set_fitness(self.fitness_score)
        # print(self.fitness_score)

    def calculate_angle_difference(self):
        angle_threshold = 30  # Umbral de ángulo para considerar un giro correcto
        forward = self.controlled_entity.car_entity.get_transform().get_forward()
        entity_direction = math.degrees(math.atan2(forward.y, forward.x))

        angle_to_checkpoint = self.controlled_entity.angle_to_next_checkpoint
        angle_difference = abs(angle_to_checkpoint - entity_direction)
        # if angle_difference < angle_threshold:
        #     return angle_difference
        return angle_difference

    # def is_turn_taken_correctly(self):
    #     angle_threshold = 30  # Umbral de ángulo para considerar un giro correcto
    #     forward = self.controlled_entity.car_entity.get_transform().get_forward()
    #     entity_direction = math.degrees(math.atan2(forward.y, forward.x))
    # 
    #     angle_to_checkpoint = self.controlled_entity.angle_to_next_checkpoint
    #     if abs(angle_to_checkpoint - entity_direction) < angle_threshold:
    #         return True
    #     return False

    def select(self):
        self.controlled_entity.selected_as_provisional_parent = True

    def deselect(self):
        self.controlled_entity.selected_as_provisional_parent = False

    def select_as_parent(self):
        self.controlled_entity.selected_as_parent = True

    def deselect_as_parent(self):
        self.controlled_entity.selected_as_parent = False

    def reset(self):
        self.fitness_score = 0
        self.controlled_entity.selected_as_parent = False
        self.controlled_entity.selected_as_provisional_parent = False
        self.controlled_entity.traveled_distance = 0
        self.controlled_entity.checkpoint_number = -1
        self.controlled_entity.current_tile_type = None
        self.controlled_entity.distance_to_next_checkpoint = 10 * 16
