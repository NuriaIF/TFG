import random

import numpy as np
import pygame

from game.ai.ai_agent import AIAgent


class GeneticAlgorithm:
    def __init__(self):
        self.current_agent_index: int = 0
        self._agents: list[AIAgent] = []
        self.mutation_rate: float = 0.01
        self.generation_duration: int = 100
        self.generation_timer: int = 0
        self.parents_selected_list: list[AIAgent] = []
        self.end_of_selection: bool = False
        self.current_generation = 1
        self.elite_fraction = 0.1  # 10% of the best agents are preserved as elite
        self.best_individuals: list[tuple[AIAgent, int]] = []

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
        neural_networks = [agent.neural_network for agent in self._agents]
        num_agents = len(self._agents)
        next_generation = []
        # parent1, parent2 = self.parents_selected_list

        # Elitism: Preserve the top agents
        elitism_count = int(self.elite_fraction * num_agents)
        # elite_agents = self._agents[:num_elite]
        # next_generation.extend(elite_agents)
        next_generation.extend(sorted(self._agents, key=lambda x: x.fitness_score, reverse=True)[:elitism_count])

        while len(next_generation) < num_agents:
            parent1, parent2 = self.tournament_selection(), self.tournament_selection()
            child_genome = self._crossover(parent1.get_genome(), parent2.get_genome())
            child_genome = self._mutate(child_genome)
            index = len(next_generation)
            neural_network = neural_networks[index]
            neural_network.set_parameters(child_genome)
            next_generation.append(AIAgent(self._agents[index].controlled_entity, neural_network))

        self._agents = next_generation
        self.current_generation += 1

    def _crossover(self, genome1, genome2):
        if len(genome1) != len(genome2):
            raise ValueError("Genomes must have the same length")

        # One-point crossover
        # crossover_point = np.random.randint(1, len(genome1))
        # child_genome = np.concatenate((genome1[:crossover_point], genome2[crossover_point:]))
        # return child_genome

        # Uniform crossover
        child_genome = np.empty(len(genome1))
        for i in range(len(genome1)):
            child_genome[i] = genome1[i] if np.random.rand() > 0.5 else genome2[i]
        return child_genome

    def _mutate(self, genome, mutation_strength=0.1):
        for i in range(len(genome)):
            if np.random.rand() < self.mutation_rate:
                genome[i] += np.random.normal(0, mutation_strength)
        return genome

    def tournament_selection(self, k=5):
        tournament = random.sample(self._agents, k)
        parent = max(tournament, key=lambda x: x.fitness_score)
        return parent

    def select_agents(self, best_individuals: list[AIAgent] = None):
        for agent in self._agents:
            agent.evaluate_fitness()

        # num_agents = len(self._agents)
        # self._agents.sort(key=lambda x: x.fitness_score, reverse=True)
        # top_agents = self._agents[:num_agents // 2]
        # 
        # parent1 = top_agents[0]  # El mejor agente
        # parent2 = top_agents[1]  # El segundo mejor agente
        parent1 = best_individuals[0]
        parent2 = best_individuals[1]
        parent1.neural_network.save_parameters()

        self.parents_selected_list: list[AIAgent] = [parent1, parent2]
        parent1.select_as_parent()
        parent2.select_as_parent()
        self.end_of_selection = True

    def select_agents_manually(self):
        # Instead of calculation, let player select manually the parents
        # Wait until player selects parents
        for event in pygame.event.get():
            # Player press space to move into parents and enter to select one, player has to select
            # 2 parents
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self._agents[self.current_agent_index].deselect()
                    self.current_agent_index += 1
                    if self.current_agent_index >= len(self._agents):
                        self.current_agent_index = 0
                    self._agents[self.current_agent_index].select()
                if event.key == pygame.K_RETURN:
                    self.parents_selected_list.append(self._agents[self.current_agent_index])
                    self._agents[self.current_agent_index].select_as_parent()
                    # if key is return and has selected 2 parents
                    if len(self.parents_selected_list) == 2:
                        # self.generation_state = "evolving"
                        self.end_of_selection = True
        for agent in self.parents_selected_list:
            agent.deselect_as_parent()

    def get_generation_number(self):
        return self.current_generation
