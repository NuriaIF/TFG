import sys
import time

import numpy as np
import pygame

from game.ai.ai_agent import AIAgent


class GeneticAlgorithm:
    def __init__(self):
        self.current_agent_index: int = 0
        self._agents: list[AIAgent] = []
        self.mutation_rate: float = 0.05
        # self.initialization_entities_callback = initialization_callback

        self.generation_duration: int = 500
        self.generation_timer: int = 0
        # self.selection_callback = selection_callback
        # self.generation_state = "simulation"  # "simulation", "selection", "evolving"
        self.parents_selected_list: list[AIAgent] = []
        self.end_of_selection: bool = False
        self.current_generation = 0

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
        parent1, parent2 = self.parents_selected_list
        while len(next_generation) < num_agents:
            # parent1 = top_agents[0]  # El mejor agente
            # parent2 = np.random.choice(top_agents[1:], 1)[0]  # Selecciona el segundo padre al azar de los siguientes mejores agentes
            # parent2 = top_agents[1]  # El segundo mejor agente
            child_genome = self._crossover(parent1.get_genome(), parent2.get_genome())
            child_genome = self._mutate(child_genome)
            # new_car = Car(self.create_entity("entities/car", has_collider=True, is_static=False))
            # new_car.set_position(Vector2(11 * 16, 42 * 16))
            # next_generation.append(AIAgent(new_car, child_genome))
            index = len(next_generation)
            neural_network = neural_networks[index]
            neural_network.set_parameters(child_genome)
            next_generation.append(AIAgent(self._agents[index].controlled_entity, neural_network))

        # self.selection_callback()
        # for agent in top_agents:
        #     agent.deselect()
        self._agents = next_generation
        self.current_generation += 1

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

    def select_agents(self):
        for agent in self._agents:
            agent.evaluate_fitness()
            print(agent.fitness_score)

        num_agents = len(self._agents)
        self._agents.sort(key=lambda x: x.fitness_score, reverse=True)
        top_agents = self._agents[:num_agents // 2]
        # self.initialization_entities_callback()
        parent1 = top_agents[0]  # El mejor agente
        parent2 = top_agents[1]  # El segundo mejor agente
        parent1.neural_network.save_parameters()
        # parent1.select()
        # parent2.select()
        self.parents_selected_list: list[AIAgent] = [parent1, parent2]
        parent1.select()
        parent2.select()
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
