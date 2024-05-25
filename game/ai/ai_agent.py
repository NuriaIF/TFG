import math

from pygame import Vector2

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
        angle_difference, angle_penalty = self.calculate_angle_difference()

        self.fitness_score = checkpoint_reached * 16 * 10 + 16 * 10 - distance_to_next_checkpoint\
                             - angle_difference * angle_penalty

        self.controlled_entity.car_entity.set_fitness(self.fitness_score)
        print(self.fitness_score)

    def calculate_angle_difference(self):
        angle_threshold = 30  # Umbral de ángulo para considerar un giro correcto
        forward = self.controlled_entity.car_entity.get_transform().get_forward()
        entity_direction = math.degrees(math.atan2(forward.y, forward.x))

        angle_to_checkpoint = self.controlled_entity.angle_to_next_checkpoint
        angle_difference = abs(angle_to_checkpoint - entity_direction)
        if angle_difference < angle_threshold:
            return angle_difference, 0
        return angle_difference, 0.5

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
