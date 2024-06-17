import random

import numpy as np
import pygame

from game.ai.ai_agent import AIAgent
from game.ai.neural_network.neural_network import NeuralNetwork


class GeneticAlgorithm:
    """
    Genetic Algorithm class that manages the genetic algorithm
    """
    def __init__(self):
        self.current_agent_index: int = 0
        self._agents: list[AIAgent] = []
        self.mutation_rate: float = 0.01
        self.mutation_strength: float = 0.02
        self.generation_duration: int = 100
        self.generation_timer: int = 0
        self.parents_selected_list: list[AIAgent] = []
        self.end_of_selection: bool = False
        self.current_generation = 1
        self.elite_fraction = 0.2  # 10% of the best agents are preserved as elite
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
        # self.elitism_list = []
        # neural_networks = [agent.neural_network for agent in self._agents]
        # num_agents = len(self._agents)
        # next_generation = []
        # 
        # # Elitism: Preserve the top agents
        # elitism_count = int(self.elite_fraction * num_agents)
        # # next_generation.extend(sorted(self._agents, key=lambda x: x.best_fitness, reverse=True)[:elitism_count])
        # agents_ordered = sorted(self._agents, key=lambda x: x.best_fitness, reverse=True)
        # next_generation.extend(agents_ordered[:elitism_count])
        # top_agent = sorted(self._agents, key=lambda x: x.best_fitness, reverse=True)[0]
        # top_agent.neural_network.save_parameters()
        # top_agent.save_fitness_score_log()
        # self.elitism_list = agents_ordered[:elitism_count]

        population = self._agents
        fitness_scores = [agent.best_fitness for agent in self._agents]

        # Ordenar la población por fitness score en orden descendente
        sorted_population = [x for _, x in
                             sorted(zip(fitness_scores, population), key=lambda pair: pair[0], reverse=True)]

        # Determinar el número de individuos élite a conservar
        num_elite = int(self.elite_fraction * len(population))
        next_generation = sorted_population[:num_elite]

        top_agent = sorted_population[0]
        top_agent.neural_network.save_parameters()

        # Mantener los genomas de los élites sin cambios
        for elite in next_generation:
            elite.genome = elite.get_genome().copy()

        # Generar el resto de la nueva generación
        while len(next_generation) < len(population):
            parent1 = self.tournament_selection(k=3)
            parent2 = self.tournament_selection(k=3)
            child1, child2 = self._crossover(parent1.get_genome(), parent2.get_genome())
            child1, child2 = self._mutate(child1), self._mutate(child2)
            next_generation.append(AIAgent(None, NeuralNetwork(layer_sizes=[292, 150, 60, 6], parameters=child1)))
            if len(next_generation) < len(population):
                next_generation.append(AIAgent(None, NeuralNetwork(layer_sizes=[292, 150, 60, 6], parameters=child2)))

        self._agents = next_generation
        self.current_generation += 1

        # while len(next_generation) < num_agents:
        #     parent1, parent2 = self.tournament_selection(), self.tournament_selection()
        #     child_genome = self._crossover(parent1.get_genome(), parent2.get_genome())
        #     child_genome = self._mutate(child_genome)
        #     index = len(next_generation)
        #     neural_network = neural_networks[index]
        #     neural_network.set_parameters(child_genome)
        #     next_generation.append(AIAgent(self._agents[index].controlled_entity, neural_network))
        # 
        # self._agents = next_generation
        # self.current_generation += 1

    def _crossover(self, genome1, genome2):
        """
        Crossover two genomes
        :param genome1: weights and biases of the neural network of the first parent
        :param genome2: weights amd biases of the neural network of the second parent
        :return: child genome
        """
        if len(genome1) != len(genome2):
            raise ValueError("Genomes must have the same length")

        # One-point crossover
        # crossover_point = np.random.randint(1, len(genome1))
        # child_genome = np.concatenate((genome1[:crossover_point], genome2[crossover_point:]))
        # return child_genome

        # Uniform crossover
        # child_genome = np.empty(len(genome1))
        # for i in range(len(genome1)):
        #     child_genome[i] = genome1[i] if np.random.rand() > 0.5 else genome2[i]
        # return child_genome
        
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

    def tournament_selection(self, k=3):
        tournament = random.sample(self._agents, k)
        parent = max(tournament, key=lambda x: x.best_fitness)
        return parent

    def select_agents(self):
        for agent in self._agents:
            agent.evaluate_fitness()

        num_agents = len(self._agents)
        agents = self._agents.copy()
        agents.sort(key=lambda x: x.best_fitness, reverse=True)
        top_agents = agents[:num_agents // 2]
        parent1, parent2 = self.tournament_selection(), self.tournament_selection()
        # parent1, parent2 = top_agents[0], top_agents[1]
        # 
        # parent1 = top_agents[0]  # El mejor agente
        # parent2 = top_agents[1]  # El segundo mejor agente
        # parent1 = best_individuals[0]
        # parent2 = best_individuals[1]
        parent1.neural_network.save_parameters()
        parent1.save_fitness_score_log()

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

    def reintroduce_diversity(self):
        for agent in self._agents:
            if np.random.rand() < 0.1:  # Reintroducción de diversidad con una probabilidad del 10%
                agent.genome = np.random.uniform(-1, 1, len(agent.get_genome())).tolist()
