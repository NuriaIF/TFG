from __future__ import annotations

import json

import numpy as np

from src.engine.ai.ai_agent import AIAgent
from src.engine.managers.entity_manager.entity_manager import EntityManager
from src.engine.managers.input_manager.input_manager import InputManager
from src.engine.managers.input_manager.key import Key
from src.engine.ai.AI_input_manager import AIInputManager
from src.game.AI.ai_state import AIState
from src.game.AI.car_ai_agent import CarAIAgent
from src.game.AI.data_collector import DataCollector
from src.engine.ai.genetic_algorithm.genetic_algorithm import GeneticAlgorithm, NEURAL_NET_LAYER_SIZES
from src.engine.ai.neural_network.neural_network import NeuralNetwork
from src.game.entities.car import Car
from src.game.AI.ai_info.chronometer import Chronometer

population_size = 15


class AIManager:
    """
    AI Manager class that manages the AI agents
    """

    def __init__(self, entity_manager: EntityManager, training=True) -> None:
        self.entity_manager: EntityManager = entity_manager
        self.current_agent_index: int = 0
        self.training: bool = training
        if training:
            self.genetic_algorithm: GeneticAlgorithm = GeneticAlgorithm()
        self._agents: list[AIAgent] = []
        self.state: AIState = AIState.SIMULATION

        self.no_improvement_counter = 0
        self.no_improvement_limit = 200

        self.fitness_scores = {}

        self.inputs = []

        self.data_collector_activated = True
        if self.data_collector_activated:
            self.data_collector = DataCollector()
        self._end_of_generation = False

        self._all_disabled = False

    def get_agents(self) -> list[AIAgent]:
        """
        Get the agents
        :return: list of AI agents
        """
        if self.training:
            return self.genetic_algorithm.get_agents()
        else:
            return self._agents

    def update(self, cars: list[Car], input_manager: InputManager = None,
               frame_chronometer: Chronometer = None) -> None:
        """
        Update the AI manager
        :param cars: list of cars
        :param input_manager: input manager
        :param frame_chronometer: frame chronometer
        """
        if not self.get_agents():
            self.create_population(cars)
        elif self.state == AIState.SIMULATION:
            self.simulate(frame_chronometer)
            if self.training:
                self.handle_user_inputs(input_manager, frame_chronometer)
        elif self.state == AIState.EVOLVING:
            self.evolve_agents(frame_chronometer)

    def simulate(self, frame_chronometer) -> None:
        """
        Simulate the AI agents
        :param frame_chronometer: frame chronometer
        """
        self._all_disabled = True
        if len(self.get_agents()) > 1:
            if self.genetic_algorithm.generation_timer.get_elapsed_time() == 0:
                self.genetic_algorithm.generation_timer.start()
        for agent in self.get_agents():
            agent.evaluate_fitness()
            if self.data_collector_activated:
                self.data_collector.collect_fitness(agent, frame_chronometer.get_elapsed_time())
            if not agent.controlled_entity.disabled:
                self.inputs = self.prepare_input(agent.controlled_entity)
                outputs = agent.neural_network.forward(self.inputs)
                # Convert outputs to commands
                agent.controlled_entity.input_manager.convert_outputs_to_commands(outputs)
                self._all_disabled = False
            else:
                agent.controlled_entity.input_manager.stop_keys()

    def evolve_agents(self, frame_chronometer) -> None:
        """
        Evolve agents
        """
        if self.data_collector_activated:
            self.data_collector.change_generation(frame_chronometer.get_elapsed_time(), self.get_agents(),
                                                  self.genetic_algorithm.current_generation)
        cars = [agent.controlled_entity for agent in self.get_agents()]
        next_generation = self.genetic_algorithm.evolve_agents()
        next_generation_agents = []
        for genome, car in zip(next_generation, cars):
            next_generation_agents.append(CarAIAgent(car, NeuralNetwork(layer_sizes=NEURAL_NET_LAYER_SIZES,
                                                                        parameters=genome)))
        self.genetic_algorithm.load_agents(next_generation_agents)
        self.state = AIState.SIMULATION
        self.genetic_algorithm.generation_timer.reset()
        self.reset(cars)
        self._end_of_generation = True
        if self.data_collector_activated:
            self.data_collector.add_top_fitness(self.genetic_algorithm.top_fitness)

    def has_generation_ended(self) -> bool:
        """
        Check if the generation has ended
        :return: True if the generation has ended, False otherwise
        """
        return self._end_of_generation

    def next_generation(self) -> None:
        """
        Go to the next generation
        """
        self._end_of_generation = False

    def prepare_input(self, car: Car) -> list[float]:
        """
        Prepare the input for the neural network
        :param car: car to get the inputs from
        :return: list of inputs for the neural network of the car
        """
        physics = self.entity_manager.get_physics(car.entity_ID)

        agent_velocity: float = physics.get_velocity()

        next_checkpoint_position = car.car_knowledge.get_next_checkpoint_position()

        car_position = self.entity_manager.get_transform(car.entity_ID).get_position()
        relative_position = (next_checkpoint_position[0] - car_position[0],
                             next_checkpoint_position[1] - car_position[1])
        max_velocity = car.accelerate_max_speed
        min_velocity = -car.base_max_speed
        normalized_velocity = (agent_velocity - min_velocity) / (max_velocity - min_velocity)
        distance = np.linalg.norm(relative_position)
        # Normalize relative vector
        if distance != 0:
            normalized_relative_position = relative_position / distance
        else:
            normalized_relative_position = np.zeros_like(relative_position)

        agent_field_of_view: list[float] = car.car_knowledge.field_of_view.get_encoded_version()
        inputs = [normalized_velocity] + list(normalized_relative_position)
        inputs.extend(agent_field_of_view)
        return inputs

    def create_population(self, cars: list[Car]) -> None:
        """
        Initialize population
        """
        if len(cars) <= 2:
            self.get_agents().append(CarAIAgent(cars[-1], NeuralNetwork(layer_sizes=NEURAL_NET_LAYER_SIZES)))
            self.get_agents()[-1].neural_network.load_parameters()
            return
        agents = self._create_new_population(cars)  # or self._load_agents_from_file(cars)
        self.genetic_algorithm.load_agents(agents)

    def reset(self, cars: list[Car]):
        """
        Reset the agents
        :param cars: list of cars
        """
        for agent, car in zip(self.get_agents(), cars):
            agent.reset(car)

    def _create_new_population(self, cars):
        agents: list[AIAgent] = []
        for i in range(population_size):
            agents.append(CarAIAgent(cars[i], NeuralNetwork(layer_sizes=NEURAL_NET_LAYER_SIZES)))
            agents[i].neural_network.load_parameters()
        return agents

    def handle_user_inputs(self, input_manager, frame_chronometer):
        # check if generation is over
        if input_manager.is_key_down(Key.K_S):
            cars = [agent.controlled_entity for agent in self.get_agents()]
            if self.data_collector_activated:
                self.data_collector.save_data(frame_chronometer.get_elapsed_time())
        # detect keys pressed, 'N' for next generation
        if (input_manager.is_key_down(Key.K_N)
                or self._all_disabled
                or self.genetic_algorithm.generation_timer.get_elapsed_time() >
                self.genetic_algorithm.generation_duration):
            # before going to the next generation, save fitness scores
            self.fitness_scores[self.genetic_algorithm.current_generation] = []
            for agent in self.get_agents():
                self.fitness_scores[self.genetic_algorithm.current_generation].append(agent.fitness_score)
            with open('fitness_scores.json', 'w') as f:
                json.dump(self.fitness_scores, f)

            self.no_improvement_counter = 0
            self.state = AIState.EVOLVING
