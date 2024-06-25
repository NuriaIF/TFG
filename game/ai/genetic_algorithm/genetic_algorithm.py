import random

import numpy as np
import pygame

from game.ai.ai_agent import AIAgent
from game.ai.neural_network.neural_network import NeuralNetwork

NEURAL_NET_LAYER_SIZES = [149, 100, 60, 6]

class GeneticAlgorithm:
    """
    Genetic Algorithm class that manages the genetic algorithm
    """
    def __init__(self):
        self.current_agent_index: int = 0
        self._agents: list[AIAgent] = []
        self.mutation_rate: float = 0.1
        self.mutation_strength: float = 0.2
        self.generation_duration: int = 100
        self.generation_timer: int = 0
        self.parents_selected_list: list[AIAgent] = []
        self.end_of_selection: bool = False
        self.current_generation = 1
        self.elite_fraction = 0.13  # 13% of the best agents are preserved as elite
        self.best_individuals: list[tuple[AIAgent, int]] = []
        self.elitism_list: list[AIAgent] = []

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
            # parent1 = self.tournament_selection(sorted_population)
            # parent2 = self.tournament_selection(sorted_population)
            # child1, child2 = self._crossover(parent1.get_genome(), parent2.get_genome())
            child1, child2 = self._mutate(parent1.get_genome()), self._mutate(parent1.get_genome())
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
