import numpy as np

from game.ai.ai_agent import AIAgent
from game.entities.car import Car


class GeneticAlgorithm:
    def __init__(self, initialization_callback):
        self._agents: list[AIAgent] = []
        self.mutation_rate = 0.1
        self.initialization_entities_callback = initialization_callback

    def get_agents(self) -> list[AIAgent]:
        """
        Get the agents of the genetic algorithm
        :return: list[AIAgent]
        """
        return self._agents

    def evolve_agents(self):
        for agent in self._agents:
            agent.evaluate_fitness()

        num_agents = len(self._agents)
        self._agents.sort(key=lambda x: x.fitness_score, reverse=True)
        top_agents = self._agents[:num_agents // 2]

        next_generation = []
        neural_networks = [agent.neural_network for agent in self._agents]
        self.initialization_entities_callback()
        while len(next_generation) < num_agents:
            parent1, parent2 = np.random.choice(top_agents, 2)
            child_genome = self._crossover(parent1.get_genome(), parent2.get_genome())
            child_genome = self._mutate(child_genome)
            # new_car = Car(self.create_entity("entities/car", has_collider=True, is_static=False))
            # new_car.set_position(Vector2(11 * 16, 42 * 16))
            # next_generation.append(AIAgent(new_car, child_genome))
            index = len(next_generation)
            neural_network = neural_networks[index]
            neural_network.set_parameters(child_genome)
            next_generation.append(AIAgent(self._agents[index].controlled_entity, neural_network))

        self._agents = next_generation

    def _crossover(self, genome1, genome2):
        if len(genome1) != len(genome2):
            raise ValueError("Genomes must have the same length")

        child_genome = np.empty(len(genome1))
        crossover_point = np.random.randint(1, len(genome1))  # Crossover de un punto
        child_genome[:crossover_point] = genome1[:crossover_point]
        child_genome[crossover_point:] = genome2[crossover_point:]

        return child_genome

    def _mutate(self, genome, mutation_strength=0.1):
        for i in range(len(genome)):
            if np.random.rand() < self.mutation_rate:
                genome[i] += np.random.normal(0, mutation_strength)
        return genome
