import numpy as np

from game.ai.ai_agent import AIAgent


class GeneticAlgorithm:
    def __init__(self, agents):
        self.agents: list[AIAgent] = agents
        self.mutation_rate = 0.1

    def get_agents(self):
        return self.agents

    def evolve_agents(self):
        for agent in self.agents:
            agent.evaluate_fitness()

        num_agents = len(self.agents)
        self.agents.sort(key=lambda x: x.fitness, reverse=True)
        top_agents = self.agents[:num_agents // 2]

        next_generation = []
        while len(next_generation) < num_agents:
            parent1, parent2 = np.random.choice(top_agents, 2)
            child_genome = self._crossover(parent1.get_genome(), parent2.get_genome())
            self._mutate(child_genome)
            next_generation.append(AIAgent(child_genome))

        self.agents = next_generation

    def _crossover(self, genome1, genome2):
        if len(genome1) != len(genome2):
            raise ValueError("Los genomas deben tener el mismo tamaño")

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
