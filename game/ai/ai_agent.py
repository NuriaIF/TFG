class AIAgent():
    def __init__(self, controlled_entity, neural_network):
        self.neural_network = neural_network
        self.fitness_score = 0
        self.controlled_entity = controlled_entity

    def get_genome(self):  # Genome is neural network weights and biases
        # return np.concatenate([param.data.numpy().flatten() for param in self.neural_network.get_parameters()])
        return self.neural_network.get_parameters()

    def evaluate_fitness(self):
        pass