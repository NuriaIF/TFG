"""
This module contains the GeneticAlgorithm class that manages the genetic algorithm
"""

import numpy as np

from src.engine.ai.ai_agent import AIAgent
from src.game.ai.ai_info.chronometer import Chronometer


class GeneticAlgorithm:
    """
    Genetic Algorithm class that manages the genetic algorithm
    """

    def __init__(self):
        self._agents: list[AIAgent] = []
        self.mutation_rate: float = 0.04
        self.mutation_strength: float = 0.1
        self.generation_duration: int = 300
        self.generation_timer: Chronometer = Chronometer()
        self.end_of_selection: bool = False
        self.current_generation = 1
        self.elite_fraction = 0.13  # 13% of the best agents are preserved as elite
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

    def evolve_agents(self) -> list[np.ndarray]:
        """
        Evolve the agents and return the new population of agents for the next generation based on the fitness scores
        of the current generation and the genetic algorithm parameters
        :return: genomes of the new population of agents
        """
        population = self.get_agents()

        # Sort the population by fitness score in descending order
        sorted_population = sorted(population, key=lambda x: x.fitness_score, reverse=True)
        top_agent = sorted_population[0]
        top_agent.neural_network.save_parameters()
        self.top_fitness = top_agent.fitness_score

        # Determine number of elite agents to keep
        num_elite = int(round(self.elite_fraction * len(population)))
        if self.elite_fraction > 0 and len(population) > 0:
            num_elite = max(1, num_elite)
        elite = sorted_population[:num_elite]

        next_generation = []
        # Preserve the elite agents for the next generation without changes
        for agent in elite:
            genome_copy = agent.get_genome().copy()
            next_generation.append(genome_copy)
        parent1 = sorted_population[0]
        parent2 = sorted_population[1]
        # Crossover and mutate for generating the rest of the population
        while len(next_generation) < len(population):
            child1, child2 = self._crossover(parent1.get_genome().copy(), parent2.get_genome().copy())
            child1, child2 = self._mutate(child1), self._mutate(child2)
            next_generation.append(child1)
            if len(next_generation) < len(population):
                next_generation.append(child2)
        self.mutation_rate *= 0.99
        self.mutation_strength *= 0.99

        self.current_generation += 1
        return next_generation

    @staticmethod
    def _crossover(genome1, genome2):
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
        """
        Mutate the genome of an agent
        :param genome: weights and biases of the neural network of the agent
        :return: mutated genome
        """
        genome_copy = genome.copy()
        for i in range(len(genome)):
            if np.random.rand() < self.mutation_rate:
                genome_copy[i] += np.random.normal(0, self.mutation_strength)
        return genome_copy
