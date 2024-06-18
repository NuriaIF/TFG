from __future__ import annotations

import json

import numpy as np
from pygame import Vector2

from engine.managers.input_manager.input_manager import InputManager
from engine.managers.input_manager.key import Key
from game.ai.ai_agent import AIAgent
from game.ai.ai_input_manager import AIInputManager
from game.ai.neural_network.neural_network import NeuralNetwork
from game.entities.car import Car
from game.ai.genetic_algorithm.genetic_algorithm import GeneticAlgorithm


class AIManager:
    """
    AI Manager class that manages the AI agents
    """

    def __init__(self, initialization_callback, training=True) -> None:
        self.current_agent_index: int = 0
        self.population_size: int = 20
        self.training: bool = training
        if training:
            self.genetic_algorithm: GeneticAlgorithm = GeneticAlgorithm()
            self.initialization_entities_callback = initialization_callback
        self._agents: list[AIAgent] = []
        self.state: str = "simulation"

        self.best_individuals: list[AIAgent] = []

        self.no_improvement_counter = 0
        self.no_improvement_limit = 200

        self.fitness_scores = {}

        self.inputs = []


    def get_population_size(self) -> int:
        """
        Get the population size
        :return: an integer representing the population size
        """
        return self.population_size

    def get_agents(self) -> list[AIAgent]:
        """
        Get the agents
        :return: list of AI agents
        """
        if self.training:
            return self.genetic_algorithm.get_agents()
        else:
            return self._agents

    def update(self, cars: list[Car], input_manager: InputManager = None) -> None:
        """
        Update the AI manager
        :param cars: list of cars
        :param input_manager: input manager
        """
        if not self.get_agents():
            self.create_population(cars)
        if self.state == "simulation":
            self.simulate(input_manager)
        elif self.state == "selection":
            self.select_agents()
        elif self.state == "evolving":
            self.evolve_agents()

    def simulate(self, input_manager: InputManager) -> None:
        """
        Simulate the AI agents
        :param input_manager: input manager to get the keys pressed
        """
        # for agent in self.ai_agents:
        #     self.prepare_input(agent, game, tilemap)
        if self.state == "simulation":
            agents_copy = self.get_agents().copy()
            agents_copy.sort(key=lambda x: x.best_fitness, reverse=True)
            for agent in self.get_agents():
                agent.evaluate_fitness()
                # if self.best_fitness < agent.fitness_score and self.training:
                #     self.best_fitness = agent.fitness_score
                #     if not self.best_individuals[0] == agent:
                #         self.best_fitness = agent.fitness_score
                #         self.best_individuals[1] = self.best_individuals[0]
                #         self.best_individuals[0] = agent
                self.best_individuals = agents_copy[:2]
                self.inputs = self.prepare_input(agent.controlled_entity)
                outputs = agent.neural_network.forward(self.inputs)
                # TODO: Convert outputs to commands
                agent.ai_input_manager.convert_outputs_to_commands(outputs)

            if not self.training:
                return

        # Evolve best agent
        # TODO: check if generation is over
        # check if generation is over
        self.genetic_algorithm.generation_timer += 1
        # detect keys pressed, 'N' for next generation
        # key_pressed = False
        # if self.genetic_algorithm.generation_timer >= self.genetic_algorithm.generation_duration:
        all_less_than_zero = True
        all_stand_still = True
        # for agent in self.get_agents():
        #     if agent.fitness_score > 0:
        #         all_less_than_zero = False
        #     if agent.controlled_entity.car_entity.get_physics().get_velocity() > 0.1:
        #         all_stand_still = False
        # Change generation when there is not improvement anymore
        current_best_fitness = max(agent.fitness_score for agent in self.get_agents())
        global_best_fitness = max(agent.best_fitness for agent in self.get_agents())
        if global_best_fitness > current_best_fitness:
            self.no_improvement_counter += 1
        else:
            self.no_improvement_counter = 0
        if input_manager.is_key_down(Key.K_N) or self.no_improvement_counter >= self.no_improvement_limit:
            # antes de pasar a la siguiente generacion
            self.fitness_scores[self.genetic_algorithm.current_generation] = []
            for agent in self.get_agents():
                self.fitness_scores[self.genetic_algorithm.current_generation].append(agent.best_fitness)
            with open('fitness_scores.json', 'w') as f:
                json.dump(self.fitness_scores, f)

            self.no_improvement_counter = 0
            self.state = "evolving" # "selection"
            for agent in self.get_agents():
                agent.ai_input_manager.stop_keys()
        # if input_manager.is_key_down(Key.K_N) or (all_less_than_zero and self.genetic_algorithm.generation_timer >= 50) \
        #         or (all_stand_still and self.genetic_algorithm.generation_timer >= 50):
        #     self.state = "selection"
        #     for agent in self.get_agents():
        #         agent.ai_input_manager.stop_keys()

    def select_agents(self) -> None:
        """
        Select agents to evolve
        """
        self.genetic_algorithm.select_agents()
        if self.genetic_algorithm.end_of_selection:
            self.state = "evolving"
            self.genetic_algorithm.end_of_selection = False

    def evolve_agents(self) -> None:
        """
        Evolve agents
        """
        self.genetic_algorithm.evolve_agents()
        self.state = "simulation"
        self.genetic_algorithm.generation_timer = 0
        self.initialization_entities_callback()

    def prepare_input(self, car: Car) -> list[float]:
        """
        Prepare the input for the neural network
        :param car: car to get the inputs from
        :return: list of inputs for the neural network of the car
        """
        entity = car.car_entity
        agent_forward: Vector2 = entity.get_transform().get_forward()
        agent_velocity: float = entity.get_physics().get_velocity()
        agent_acceleration: float = entity.get_physics().get_acceleration()

        next_checkpoint_position = car.car_knowledge.get_next_checkpoint_position()
        car_in_tile_position = car.car_knowledge.get_field_of_view().get_nearest_tile().tile_entity.get_transform().get_position()
        relative_position = (
            next_checkpoint_position[0] - car_in_tile_position[0],
            next_checkpoint_position[1] - car_in_tile_position[1]
        )
        max_velocity = car.accelerate_max_speed
        min_velocity = -car.base_max_speed
        max_acceleration = car.engine_force / car.mass
        min_acceleration = -car.engine_force / car.mass
        normalized_velocity = (agent_velocity - min_velocity) / (max_velocity - min_velocity)
        normalized_acceleration = (agent_acceleration - min_acceleration) / (max_acceleration - min_acceleration)
        distance = np.linalg.norm(relative_position)
        # Normalize relative vector
        if distance != 0:
            normalized_relative_position = relative_position / distance
        else:
            normalized_relative_position = np.zeros_like(relative_position)

        agent_field_of_view: list[float] = car.car_knowledge.field_of_view.get_encoded_version()
        inputs = [normalized_velocity, normalized_acceleration] + list(normalized_relative_position)
        inputs.extend(agent_field_of_view)
        return inputs

    def create_population(self, cars: list[Car]) -> None:
        """
        Initialize population
        """
        # or load agents from file
        # self._load_agents_from_file()
        if len(cars) == 1:
            self.get_agents().append(AIAgent(cars[0], NeuralNetwork(layer_sizes=[292, 150, 60, 6])))
            self.get_agents()[0].neural_network.load_parameters()
            return
        agents = self._create_new_population(cars)  # or self._load_agents_from_file(cars)
        self.genetic_algorithm.load_agents(agents)
        agents_copy = self.get_agents().copy()
        agents_copy.sort(key=lambda x: x.best_fitness, reverse=True)
        self.best_individuals = agents_copy[:2]

    def get_ai_input_manager_of(self, car: Car) -> AIInputManager:
        """
        Get the AI input manager of the car
        :param car: car to get the AI input manager
        :return: AI input manager of the car
        """
        for agent in self.get_agents():
            if agent.controlled_entity == car:
                return agent.ai_input_manager

    def reset(self, cars: list[Car]):
        """
        Reset the agents
        :param cars: list of cars
        """
        for agent, car in zip(self.get_agents(), cars):
            agent.reset(car)

    def _create_new_population(self, cars):
        return [AIAgent(cars[i], NeuralNetwork(layer_sizes=[292, 150, 60, 6])) for i in range(self.population_size)]

    def _load_agents_from_file(self, cars):
        agents = []
        for i in range(self.population_size):
            agent = AIAgent(cars[i], NeuralNetwork(layer_sizes=[292, 150, 60, 6]))
            agent.neural_network.load_parameters()
            agents.append(agent)
        return agents
