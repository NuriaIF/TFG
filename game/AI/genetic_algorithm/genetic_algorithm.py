import numpy as np

from game.AI.AI_agent import AIAgent
from game.AI.neural_network.neural_network import NeuralNetwork
from game.AI.ai_info.chronometer import Chronometer

NEURAL_NET_LAYER_SIZES = [147, 32, 6]


class GeneticAlgorithm:
    """
    Genetic Algorithm class that manages the genetic algorithm
    """

    def __init__(self):
        self.current_agent_index: int = 0
        self._agents: list[AIAgent] = []
        self.mutation_rate: float = 0.04
        self.mutation_strength: float = 0.1
        self.generation_duration: int = 300
        self.generation_timer: Chronometer = Chronometer()
        self.parents_selected_list: list[AIAgent] = []
        self.end_of_selection: bool = False
        self.current_generation = 1
        self.elite_fraction = 0.13  # 13% of the best agents are preserved as elite
        self.elitism_list: list[AIAgent] = []
        self.top_fitness = 0

    def load_agents(self, agents: list[AIAgent]):
        """
        Load the agents of the genetic algorithm
        :param agents:
        """
        self._agents = agents

    def get_agents(self) -> list[AIAgent]:
        """
        Get the agents of the genetic algorithm
        :return: list[AIAgent]
        """
        return self._agents

    def evolve_agents(self):
        """
        Evolve the agents
        """
        population = self.get_agents()

        # Ordenar la población por fitness score en orden descendente
        sorted_population = sorted(population, key=lambda x: x.fitness_score, reverse=True)
        top_agent = sorted_population[0]
        top_agent.neural_network.save_parameters()
        self.top_fitness = top_agent.fitness_score

        # Determinar el número de individuos élite a conservar
        num_elite = int(round(self.elite_fraction * len(population)))
        if self.elite_fraction > 0 and len(population) > 0:
            num_elite = max(1, num_elite)
        elite = sorted_population[:num_elite]

        next_generation = []
        # Mantener los genomas de los élites sin cambios
        for agent in elite:
            genome_copy = agent.get_genome().copy()
            next_generation.append(AIAgent(None, NeuralNetwork(layer_sizes=NEURAL_NET_LAYER_SIZES,
                                                               parameters=genome_copy)))
        parent1 = sorted_population[0]
        parent2 = sorted_population[1]
        # Generar el resto de la nueva generación
        while len(next_generation) < len(population):
            child1, child2 = self._crossover(parent1.get_genome().copy(), parent2.get_genome().copy())
            child1, child2 = self._mutate(child1), self._mutate(child2)
            next_generation.append(AIAgent(None, NeuralNetwork(layer_sizes=NEURAL_NET_LAYER_SIZES,
                                                               parameters=child1)))
            if len(next_generation) < len(population):
                next_generation.append(AIAgent(None, NeuralNetwork(layer_sizes=NEURAL_NET_LAYER_SIZES,
                                                                   parameters=child2)))
        self.mutation_rate *= 0.99
        self.mutation_strength *= 0.99

        self._agents = next_generation
        self.current_generation += 1

    def _crossover(self, genome1, genome2):
        """
        Crossover two genomes
        :param genome1: weights and biases of the neural network of the first parent
        :param genome2: weights amd biases of the neural network of the second parent
        :return: child genome
        """
        if len(genome1) != len(genome2):
            raise ValueError("Genomes must have the same length")

        # One-point crossover with 2 children
        crossover_point = np.random.randint(1, len(genome1))
        child_genome1 = np.concatenate((genome1[:crossover_point], genome2[crossover_point:]))
        child_genome2 = np.concatenate((genome2[:crossover_point], genome1[crossover_point:]))
        return child_genome1, child_genome2

    def _crossover(self, genome1, genome2):
        """
        Crossover two genomes
        :param genome1: weights and biases of the neural network of the first parent
        :param genome2: weights amd biases of the neural network of the second parent
        :return: child genome
        """
        if len(genome1) != len(genome2):
            raise ValueError("Genomes must have the same length")

        # Uniform crossover
        child_genome1 = np.array([g1 if np.random.rand() < 0.5 else g2 for g1, g2 in zip(genome1, genome2)])
        child_genome2 = np.array([g1 if np.random.rand() < 0.5 else g2 for g1, g2 in zip(genome1, genome2)])
        return child_genome1, child_genome2

    def _mutate(self, genome):
        for i in range(len(genome)):
            if np.random.rand() < self.mutation_rate:
                genome[i] += np.random.normal(0, self.mutation_strength)
        return genome

    # def tournament_selection(self, sorted_population, tournament_size=4):
    #     tournament = random.sample(sorted_population, tournament_size)
    #     parent = max(tournament, key=lambda x: x.fitness_score)
    #     return parent
    def tournament_selection(self, sorted_population, tournament_size=4):
        # Selección por torneo mejorada que favorece ligeramente a los más aptos
        probabilities = self.calculate_probabilities(sorted_population)
        tournament = np.random.choice(sorted_population, tournament_size, replace=False, p=probabilities)
        parent = max(tournament, key=lambda x: x.fitness_score)
        return parent

    def calculate_probabilities(self, sorted_population):
        """
        Calculate the probabilities of selection for each individual in the sorted population.

        The probabilities are calculated in such a way that individuals with higher fitness
        (at the beginning of the sorted list) have a higher probability of being selected.
        This is done by assigning a probability inversely proportional to their position in
        the sorted list.

        The method ensures that the selection process is biased towards better performing
        individuals, but still allows less fit individuals a chance to be selected, thereby
        maintaining genetic diversity within the population.

        :param sorted_population: List of individuals sorted by fitness in descending order.
        :return: List of probabilities corresponding to each individual in the sorted population.
        """
        total = sum(range(1, len(sorted_population) + 1))
        return [(len(sorted_population) - i) / total for i in range(len(sorted_population))]

    # def roulette_wheel_selection(self, population):
    #     fitness_scores = [agent.fitness_score for agent in population]
    #     min_fitness = min(fitness_scores)
    #     if min_fitness < 0:
    #         fitness_scores = [fitness - min_fitness for fitness in fitness_scores]
    #
    #     total_fitness = sum(fitness_scores)
    #     selection_probs = [fitness / total_fitness for fitness in fitness_scores]
    #
    #     selected_index = np.random.choice(len(population), p=selection_probs)
    #     return population[selected_index]

    def get_generation_number(self):
        return self.current_generation

    def reintroduce_diversity(self):
        for agent in self._agents:
            if np.random.rand() < 0.1:  # Reintroducción de diversidad con una probabilidad del 10%
                agent.genome = np.random.uniform(-1, 1, len(agent.get_genome())).tolist()
