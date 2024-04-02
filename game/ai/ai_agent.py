class AIAgent():
    def __init__(self, controlled_entity, neural_network):
        self.neural_network = neural_network
        self.fitness_score = 0
        self.controlled_entity = controlled_entity

    def get_genome(self):  # Genome is neural network weights and biases
        # return np.concatenate([param.data.numpy().flatten() for param in self.neural_network.get_parameters()])
        return self.neural_network.get_parameters()

    def evaluate_fitness(self):
        # TODO: get the checkpoint number of the car
        self.fitness_score = self.controlled_entity.checkpoint_number
        # TODO: get the distance to the next checkpoint
        # TODO: reward the agent for going fast
        # TODO: penalize the agent for going off track
        # TODO: reward the agent for staying on track
        # TODO: reward the agent for not crashing
        # TODO: reward the agent for not going backwards
        # TODO: reward the agent for not running over pedestrians
