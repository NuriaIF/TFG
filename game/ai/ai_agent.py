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
        self.fitness_score = self.controlled_entity.checkpoint_number * 10
        # TODO: reward the agent for staying on track
        self.fitness_score -= self.controlled_entity.current_tile_type.value
        # print(self.controlled_entity.current_tile_type)
        # TODO: get traveled distance
        # self.fitness_score += self.controlled_entity.traveled_distance
        # TODO: reward the agent for going forward

        # TODO: get the distance to the next checkpoint
        # self.fitness_score -= self.controlled_entity.distance_to_next_checkpoint
        # TODO: reward the agent for going fast
        # TODO: penalize the agent for going off track
        # TODO: reward the agent for not crashing
        # TODO: reward the agent for not going backwards
        # TODO: reward the agent for not running over pedestrians

    def select(self):
        self.controlled_entity.selected_as_provisional_parent = True

    def deselect(self):
        self.controlled_entity.selected_as_provisional_parent = False

    def select_as_parent(self):
        self.controlled_entity.selected_as_parent = True

    def deselect_as_parent(self):
        self.controlled_entity.selected_as_parent = False
